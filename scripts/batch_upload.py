"""
Batch Model Uploader for AR Platform.

Uploads multiple 3D models from a directory using metadata from a JSON file.

Features:
- Process multiple models in sequence
- Progress tracking with tqdm
- Summary report (successes/failures)
- Continue on error (doesn't stop batch on single failure)
- Detailed logging

Usage:
    python batch_upload.py --dir models/ --metadata models/metadata.json

Metadata JSON Format:
[
    {
        "filename": "burger_classic.glb",
        "model_id": "BURGER_001",
        "product_name": "Classic Burger",
        "category": "food",
        "price": 8.99,
        "client_id": "RESTAURANT_001"
    },
    ...
]
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.upload_model import ModelUploader
from tqdm import tqdm

logger = logging.getLogger(__name__)


class BatchUploader:
    """
    Batch upload multiple 3D models to AR platform.

    Attributes:
        uploader: ModelUploader instance
        results: List of upload results
    """

    def __init__(self):
        """Initialize BatchUploader."""
        self.uploader = ModelUploader()
        self.results: List[Dict[str, Any]] = []

    def batch_upload(
        self,
        models_dir: str,
        metadata_file: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Upload multiple models from directory.

        Args:
            models_dir: Directory containing GLB files
            metadata_file: JSON file with model metadata
            overwrite: If True, overwrite existing models

        Returns:
            Summary dictionary with:
            {
                'total': int,
                'success_count': int,
                'failure_count': int,
                'results': list,
                'duration_seconds': float
            }
        """
        start_time = datetime.now()
        logger.info(f"Starting batch upload from: {models_dir}")

        # Load metadata
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
        except FileNotFoundError:
            logger.error(f"Metadata file not found: {metadata_file}")
            return self._create_summary(start_time)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metadata file: {e}")
            return self._create_summary(start_time)

        if not isinstance(metadata_list, list):
            logger.error("Metadata file must contain a JSON array")
            return self._create_summary(start_time)

        logger.info(f"Loaded metadata for {len(metadata_list)} models")

        # Process each model with progress bar
        for metadata in tqdm(metadata_list, desc="Uploading models", unit="model"):
            result = self._upload_single_model(
                models_dir=models_dir,
                metadata=metadata,
                overwrite=overwrite
            )
            self.results.append(result)

        # Generate summary
        summary = self._create_summary(start_time)
        self._print_summary(summary)
        self._save_summary(summary)

        return summary

    def _upload_single_model(
        self,
        models_dir: str,
        metadata: Dict[str, Any],
        overwrite: bool
    ) -> Dict[str, Any]:
        """
        Upload a single model.

        Args:
            models_dir: Directory containing GLB files
            metadata: Model metadata dictionary
            overwrite: Whether to overwrite existing models

        Returns:
            Upload result dictionary
        """
        try:
            # Validate metadata has required fields
            if 'filename' not in metadata:
                return {
                    'success': False,
                    'error': 'Missing filename in metadata',
                    'model_id': metadata.get('model_id', 'unknown')
                }

            # Build full path
            filename = metadata.pop('filename')  # Remove filename from metadata
            glb_path = Path(models_dir) / filename

            if not glb_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {glb_path}',
                    'model_id': metadata.get('model_id', 'unknown')
                }

            # Upload
            result = self.uploader.upload_model(
                glb_path=str(glb_path),
                metadata=metadata,
                overwrite=overwrite
            )

            return result

        except Exception as e:
            logger.exception(f"Unexpected error uploading model: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_id': metadata.get('model_id', 'unknown')
            }

    def _create_summary(self, start_time: datetime) -> Dict[str, Any]:
        """
        Create summary of batch upload results.

        Args:
            start_time: When batch upload started

        Returns:
            Summary dictionary
        """
        success_count = sum(1 for r in self.results if r.get('success'))
        failure_count = len(self.results) - success_count

        duration = (datetime.now() - start_time).total_seconds()

        summary = {
            'total': len(self.results),
            'success_count': success_count,
            'failure_count': failure_count,
            'duration_seconds': round(duration, 2),
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }

        return summary

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """
        Print summary to console.

        Args:
            summary: Summary dictionary
        """
        print("\n" + "=" * 60)
        print("BATCH UPLOAD SUMMARY")
        print("=" * 60)
        print(f"Total models: {summary['total']}")
        print(f"✅ Successful: {summary['success_count']}")
        print(f"❌ Failed: {summary['failure_count']}")
        print(f"Duration: {summary['duration_seconds']}s")

        if summary['failure_count'] > 0:
            print("\nFailed uploads:")
            for result in summary['results']:
                if not result.get('success'):
                    model_id = result.get('model_id', 'unknown')
                    error = result.get('error', 'Unknown error')
                    print(f"  - {model_id}: {error}")

        print("=" * 60)

    def _save_summary(self, summary: Dict[str, Any]) -> str:
        """
        Save summary to JSON file.

        Args:
            summary: Summary dictionary

        Returns:
            Path to saved summary file
        """
        # Create reports directory if it doesn't exist
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = reports_dir / f'batch_upload_{timestamp}.json'

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Summary saved to: {summary_file}")
        print(f"\nSummary saved to: {summary_file}")

        return str(summary_file)


def create_metadata_template(output_file: str = 'models/metadata_template.json'):
    """
    Create a metadata template JSON file.

    Args:
        output_file: Path where template will be saved
    """
    template = [
        {
            "filename": "example_burger.glb",
            "model_id": "BURGER_001",
            "product_name": "Classic Burger",
            "category": "food",
            "subcategory": "burger",
            "price": 8.99,
            "currency": "USD",
            "description": "Delicious classic beef burger with fresh lettuce and tomatoes",
            "client_id": "RESTAURANT_001",
            "polygon_count": 15000,
            "texture_resolution": "2048x2048",
            "tags": ["burger", "beef", "american"]
        },
        {
            "filename": "example_pizza.glb",
            "model_id": "PIZZA_001",
            "product_name": "Margherita Pizza",
            "category": "food",
            "subcategory": "pizza",
            "price": 12.99,
            "currency": "USD",
            "description": "Traditional Italian pizza with tomato sauce, mozzarella, and basil",
            "client_id": "RESTAURANT_001",
            "polygon_count": 20000,
            "texture_resolution": "2048x2048",
            "tags": ["pizza", "italian", "vegetarian"]
        }
    ]

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata template created: {output_file}")
    print("\nEdit this file with your model information, then run:")
    print(f"  python batch_upload.py --dir models/ --metadata {output_file}")


def main():
    """CLI interface for batch upload."""
    parser = argparse.ArgumentParser(
        description='Batch upload 3D models to AR platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create metadata template
  python batch_upload.py --create-template

  # Batch upload models
  python batch_upload.py --dir models/ --metadata models/metadata.json

  # Batch upload with overwrite
  python batch_upload.py --dir models/ --metadata models/metadata.json --overwrite
        """
    )

    parser.add_argument(
        '--dir',
        help='Directory containing GLB files'
    )
    parser.add_argument(
        '--metadata',
        help='JSON file with model metadata'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing models'
    )
    parser.add_argument(
        '--create-template',
        action='store_true',
        help='Create metadata template file'
    )
    parser.add_argument(
        '--template-output',
        default='models/metadata_template.json',
        help='Output path for template (default: models/metadata_template.json)'
    )

    args = parser.parse_args()

    # Handle template creation
    if args.create_template:
        create_metadata_template(args.template_output)
        sys.exit(0)

    # Validate required arguments
    if not args.dir or not args.metadata:
        parser.print_help()
        print("\n❌ Error: --dir and --metadata are required")
        print("   Or use --create-template to generate a template file")
        sys.exit(1)

    # Validate directory exists
    if not Path(args.dir).is_dir():
        print(f"❌ Error: Directory not found: {args.dir}")
        sys.exit(1)

    # Validate metadata file exists
    if not Path(args.metadata).is_file():
        print(f"❌ Error: Metadata file not found: {args.metadata}")
        print("\nTip: Create a template with --create-template")
        sys.exit(1)

    # Run batch upload
    print("Starting batch upload...")
    print(f"  Models directory: {args.dir}")
    print(f"  Metadata file: {args.metadata}")
    print(f"  Overwrite mode: {args.overwrite}")
    print()

    batch_uploader = BatchUploader()
    summary = batch_uploader.batch_upload(
        models_dir=args.dir,
        metadata_file=args.metadata,
        overwrite=args.overwrite
    )

    # Exit with appropriate code
    if summary['failure_count'] == 0:
        print("\n✅ All uploads successful!")
        sys.exit(0)
    elif summary['success_count'] > 0:
        print(f"\n⚠️  Partial success: {summary['success_count']}/{summary['total']} uploaded")
        sys.exit(0)
    else:
        print("\n❌ All uploads failed")
        sys.exit(1)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
