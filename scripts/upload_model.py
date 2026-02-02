"""
Model Uploader for AR Platform.

Uploads 3D models (GLB files) to Supabase Storage and stores metadata in PostgreSQL.

Features:
- File validation before upload
- Automatic retry with exponential backoff
- Rollback on failure (delete uploaded file if metadata insert fails)
- Comprehensive error handling and logging
- Progress tracking

Usage:
    from scripts.upload_model import ModelUploader

    uploader = ModelUploader()
    result = uploader.upload_model(
        glb_path='models/burger.glb',
        metadata={
            'model_id': 'BURGER_001',
            'product_name': 'Classic Burger',
            'category': 'food',
            'client_id': 'TEST_CLIENT'
        }
    )
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_supabase_client, get_supabase_admin_client, Config
from scripts.validate_glb import GLBValidator

logger = logging.getLogger(__name__)


class ModelUploader:
    """
    Handles uploading 3D models to Supabase Storage and PostgreSQL.

    This class provides a complete upload pipeline:
    1. Validate GLB file
    2. Upload to Supabase Storage (using admin client to bypass RLS)
    3. Save metadata to PostgreSQL
    4. Rollback on failure

    Attributes:
        supabase: Supabase client instance (for database operations)
        supabase_admin: Supabase admin client (for storage operations)
        validator: GLB file validator
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize ModelUploader with Supabase client.

        Args:
            max_retries: Maximum number of retry attempts for transient failures
            retry_delay: Initial delay in seconds between retries

        Raises:
            ValueError: If Supabase credentials are missing
        """
        self.supabase = get_supabase_client()

        # Try to get admin client for storage operations (bypasses RLS)
        # Falls back to regular client if service role key not available
        try:
            self.supabase_admin = get_supabase_admin_client()
            logger.info("Using admin client for storage operations (bypasses RLS)")
        except ValueError as e:
            logger.warning(f"Service role key not available: {e}")
            logger.warning("Using regular client - storage RLS policies will apply")
            self.supabase_admin = self.supabase

        self.validator = GLBValidator()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        logger.info("ModelUploader initialized")

    def upload_model(
        self,
        glb_path: str,
        metadata: Dict[str, Any],
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a GLB file and store its metadata.

        This is the main entry point for uploading models. It orchestrates
        the entire upload process with validation, error handling, and rollback.

        Args:
            glb_path: Path to the GLB file to upload
            metadata: Dictionary containing model information
                Required fields:
                    - model_id (str): Unique identifier
                    - product_name (str): Display name
                    - category (str): Product category
                    - client_id (str): Client identifier
                Optional fields:
                    - subcategory (str)
                    - price (float)
                    - currency (str)
                    - description (str)
                    - polygon_count (int)
                    - texture_resolution (str)
                    - tags (list)
            overwrite: If True, overwrite existing model with same model_id

        Returns:
            Dictionary with upload results:
            {
                'success': True/False,
                'model_id': str,
                'public_url': str,
                'file_size_mb': float,
                'upload_time': str (ISO format),
                'error': str (only if success=False)
            }

        Raises:
            None - All exceptions are caught and returned in result dict

        Example:
            >>> uploader = ModelUploader()
            >>> result = uploader.upload_model(
            ...     glb_path='models/burger.glb',
            ...     metadata={
            ...         'model_id': 'BURGER_001',
            ...         'product_name': 'Classic Burger',
            ...         'category': 'food',
            ...         'client_id': 'TEST_CLIENT',
            ...         'price': 8.99
            ...     }
            ... )
            >>> if result['success']:
            ...     print(f"Uploaded: {result['public_url']}")
        """
        start_time = time.time()
        logger.info(f"Starting upload for: {glb_path}")

        # Step 1: Validate metadata
        try:
            self._validate_metadata(metadata)
        except ValueError as e:
            logger.error(f"Metadata validation failed: {e}")
            return {
                'success': False,
                'error': f"Invalid metadata: {str(e)}",
                'model_id': metadata.get('model_id', 'unknown')
            }

        model_id = metadata['model_id']

        # Step 2: Validate GLB file
        logger.info(f"Validating file: {glb_path}")
        is_valid, error = self.validator.validate(glb_path)
        if not is_valid:
            logger.error(f"File validation failed: {error}")
            return {
                'success': False,
                'error': error,
                'model_id': model_id
            }

        # Get file info
        file_info = self.validator.get_file_info(glb_path)

        # Step 3: Check if model already exists
        if not overwrite and self._model_exists(model_id):
            error_msg = (
                f"Model with ID '{model_id}' already exists. "
                f"Use overwrite=True to replace it."
            )
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'model_id': model_id
            }

        # Step 4: Upload to storage
        try:
            storage_path = self._generate_storage_path(
                metadata['category'],
                Path(glb_path).name
            )

            logger.info(f"Uploading to storage: {storage_path}")
            public_url = self._upload_to_storage(glb_path, storage_path)
            logger.info(f"✅ Upload successful: {public_url}")

        except Exception as e:
            logger.exception("Storage upload failed")
            return {
                'success': False,
                'error': f"Storage upload failed: {str(e)}",
                'model_id': model_id
            }

        # Step 5: Save metadata to database
        try:
            # Prepare complete metadata
            complete_metadata = {
                **metadata,
                'public_url': public_url,
                'storage_path': storage_path,
                'file_size_bytes': file_info['size_bytes'],
                'file_size_mb': file_info['size_mb'],
                'file_format': 'GLB',
                'uploaded_by': 'system',
                'is_active': True
            }

            logger.info(f"Saving metadata to database for model: {model_id}")
            self._save_metadata(complete_metadata, overwrite=overwrite)
            logger.info("✅ Metadata saved successfully")

        except Exception as db_error:
            # Rollback: Delete uploaded file
            logger.error(f"Metadata insert failed: {db_error}")
            logger.warning(f"Rolling back: Deleting uploaded file from storage")

            try:
                self._delete_from_storage(storage_path)
                logger.info("✅ Rollback successful: File deleted")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
                logger.error("WARNING: Orphaned file in storage - manual cleanup required")

            return {
                'success': False,
                'error': f"Database insert failed: {str(db_error)}",
                'model_id': model_id
            }

        # Success!
        upload_time = time.time() - start_time

        result = {
            'success': True,
            'model_id': model_id,
            'public_url': public_url,
            'file_size_mb': file_info['size_mb'],
            'upload_time': datetime.utcnow().isoformat() + 'Z',
            'duration_seconds': round(upload_time, 2)
        }

        logger.info(
            f"✅ Upload complete for {model_id} "
            f"({file_info['size_mb']}MB in {upload_time:.2f}s)"
        )

        return result

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Validate that required metadata fields are present.

        Args:
            metadata: Metadata dictionary to validate

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['model_id', 'product_name', 'category', 'client_id']

        for field in required_fields:
            if field not in metadata or not metadata[field]:
                raise ValueError(f"Required field missing: {field}")

        # Validate model_id format (alphanumeric and underscore only)
        model_id = metadata['model_id']
        if not model_id.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                f"Invalid model_id '{model_id}': "
                "Use only letters, numbers, hyphens, and underscores"
            )

        logger.debug(f"Metadata validation passed for: {model_id}")

    def _model_exists(self, model_id: str) -> bool:
        """
        Check if a model with the given ID already exists.

        Args:
            model_id: Model ID to check

        Returns:
            True if model exists, False otherwise
        """
        try:
            result = self.supabase.table('models').select('model_id').eq(
                'model_id', model_id
            ).execute()

            exists = len(result.data) > 0
            if exists:
                logger.debug(f"Model {model_id} already exists in database")
            return exists

        except Exception as e:
            logger.warning(f"Error checking if model exists: {e}")
            return False

    def _generate_storage_path(self, category: str, filename: str) -> str:
        """
        Generate storage path for the file.

        Format: {category}/{filename}
        Example: food/burger_classic.glb

        Args:
            category: Product category
            filename: Original filename

        Returns:
            Storage path string
        """
        # Sanitize category (lowercase, replace spaces with hyphens)
        clean_category = category.lower().replace(' ', '-')

        # Sanitize filename (keep extension)
        path = Path(filename)
        clean_name = path.stem.replace(' ', '_')
        storage_path = f"{clean_category}/{clean_name}{path.suffix}"

        logger.debug(f"Generated storage path: {storage_path}")
        return storage_path

    def _upload_to_storage(self, file_path: str, storage_path: str) -> str:
        """
        Upload file to Supabase Storage with retry logic.

        Args:
            file_path: Local file path
            storage_path: Destination path in storage bucket

        Returns:
            Public URL of uploaded file

        Raises:
            Exception: If upload fails after all retries
        """
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Upload attempt {attempt + 1}/{self.max_retries} "
                    f"for {storage_path}"
                )

                # Upload file (using admin client to bypass RLS)
                result = self.supabase_admin.storage.from_(Config.STORAGE_BUCKET).upload(
                    path=storage_path,
                    file=file_data,
                    file_options={"content-type": "model/gltf-binary", "upsert": "true"}
                )

                # Get public URL (using admin client)
                public_url = self.supabase_admin.storage.from_(
                    Config.STORAGE_BUCKET
                ).get_public_url(storage_path)

                return public_url

            except Exception as e:
                logger.warning(f"Upload attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Upload failed after {self.max_retries} attempts: {e}")

    def _save_metadata(
        self,
        metadata: Dict[str, Any],
        overwrite: bool = False
    ) -> None:
        """
        Save model metadata to PostgreSQL database.

        Args:
            metadata: Complete metadata dictionary
            overwrite: If True, use upsert to update existing records

        Raises:
            Exception: If database insert fails
        """
        if overwrite:
            # Upsert: Insert or update if model_id already exists
            result = self.supabase.table('models').upsert(metadata).execute()
        else:
            # Insert only
            result = self.supabase.table('models').insert(metadata).execute()

        logger.debug(f"Database insert successful for {metadata['model_id']}")

    def _delete_from_storage(self, storage_path: str) -> None:
        """
        Delete a file from Supabase Storage.

        Args:
            storage_path: Path of file to delete

        Raises:
            Exception: If deletion fails
        """
        self.supabase_admin.storage.from_(Config.STORAGE_BUCKET).remove([storage_path])
        logger.debug(f"Deleted from storage: {storage_path}")


def main():
    """
    CLI interface for uploading models.

    Usage:
        python upload_model.py <glb_file> <model_id> <product_name> <category> <client_id>

    Example:
        python upload_model.py models/burger.glb BURGER_001 "Classic Burger" food TEST_CLIENT
    """
    import argparse

    parser = argparse.ArgumentParser(description='Upload a 3D model to AR platform')
    parser.add_argument('glb_file', help='Path to GLB file')
    parser.add_argument('model_id', help='Unique model ID (e.g., BURGER_001)')
    parser.add_argument('product_name', help='Product name')
    parser.add_argument('category', help='Category (e.g., food, furniture)')
    parser.add_argument('client_id', help='Client ID')
    parser.add_argument('--price', type=float, help='Product price')
    parser.add_argument('--description', help='Product description')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite if exists')

    args = parser.parse_args()

    # Build metadata
    metadata = {
        'model_id': args.model_id,
        'product_name': args.product_name,
        'category': args.category,
        'client_id': args.client_id
    }

    if args.price:
        metadata['price'] = args.price
    if args.description:
        metadata['description'] = args.description

    # Upload
    print(f"\nUploading {args.glb_file}...")
    print("-" * 60)

    uploader = ModelUploader()
    result = uploader.upload_model(
        glb_path=args.glb_file,
        metadata=metadata,
        overwrite=args.overwrite
    )

    print("-" * 60)

    if result['success']:
        print("✅ SUCCESS!")
        print(f"\nModel ID: {result['model_id']}")
        print(f"Public URL: {result['public_url']}")
        print(f"File Size: {result['file_size_mb']}MB")
        print(f"Upload Time: {result['duration_seconds']}s")
        print("\nNext steps:")
        print(f"  1. Generate QR code: python scripts/generate_qr.py {result['model_id']}")
        print(f"  2. Test AR viewer: {Config.BASE_AR_VIEWER_URL}?model={result['model_id']}")
        sys.exit(0)
    else:
        print("❌ UPLOAD FAILED")
        print(f"\nError: {result['error']}")
        print("\nTroubleshooting:")
        print("  - Check Supabase credentials in .env")
        print("  - Verify storage bucket exists and is public")
        print("  - Run config/db_schema.sql to create database tables")
        sys.exit(1)


if __name__ == '__main__':
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
