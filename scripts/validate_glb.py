"""
GLB File Validator for AR Platform.

Validates that GLB files meet platform requirements:
- File exists and is readable
- File size is under 5MB
- File has valid GLB format (magic bytes check)

GLB Format Specification:
- First 4 bytes: 0x46546C67 ('glTF' in little-endian)
- Next 4 bytes: Version (typically 2)
- Next 4 bytes: Total file length
"""

import struct
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class GLBValidator:
    """
    Validates GLB files for AR platform requirements.

    Attributes:
        MAX_FILE_SIZE_MB: Maximum allowed file size in megabytes
        MAX_FILE_SIZE_BYTES: Maximum allowed file size in bytes
        GLB_MAGIC: Expected magic bytes for GLB format (0x46546C67)
        MIN_GLB_SIZE: Minimum size for a valid GLB file (12 bytes header)
    """

    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    GLB_MAGIC = 0x46546C67  # 'glTF' in little-endian
    MIN_GLB_SIZE = 12  # Minimum header size

    def validate(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate a GLB file against all requirements.

        Args:
            file_path: Path to the GLB file to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if file passes all checks, False otherwise
            - error_message: Empty string if valid, descriptive error if invalid

        Example:
            >>> validator = GLBValidator()
            >>> is_valid, error = validator.validate('models/burger.glb')
            >>> if not is_valid:
            ...     print(f"Validation failed: {error}")
        """
        path = Path(file_path)

        # Check 1: File existence
        is_valid, error = self._check_existence(path)
        if not is_valid:
            logger.error(f"Validation failed for {file_path}: {error}")
            return False, error

        # Check 2: File size
        is_valid, error = self._check_size(path)
        if not is_valid:
            logger.error(f"Validation failed for {file_path}: {error}")
            return False, error

        # Check 3: GLB format (magic bytes)
        is_valid, error = self._check_format(path)
        if not is_valid:
            logger.error(f"Validation failed for {file_path}: {error}")
            return False, error

        logger.info(f"✅ File validation passed: {file_path}")
        return True, ""

    def _check_existence(self, path: Path) -> Tuple[bool, str]:
        """
        Check if file exists and is readable.

        Args:
            path: Path object to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path.exists():
            return False, f"File not found: {path}"

        if not path.is_file():
            return False, f"Path is not a file: {path}"

        # Check if file is readable
        try:
            with open(path, 'rb') as f:
                f.read(1)  # Try to read 1 byte
        except PermissionError:
            return False, f"File is not readable (permission denied): {path}"
        except Exception as e:
            return False, f"Cannot access file: {path} - {str(e)}"

        return True, ""

    def _check_size(self, path: Path) -> Tuple[bool, str]:
        """
        Check file size is under the maximum limit.

        Args:
            path: Path object to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_size = path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            if file_size > self.MAX_FILE_SIZE_BYTES:
                return False, (
                    f"File too large: {file_size_mb:.2f}MB "
                    f"(max {self.MAX_FILE_SIZE_MB}MB). "
                    f"Try compressing the model using Blender or online tools."
                )

            logger.debug(f"File size OK: {file_size_mb:.2f}MB")
            return True, ""

        except Exception as e:
            return False, f"Error checking file size: {str(e)}"

    def _check_format(self, path: Path) -> Tuple[bool, str]:
        """
        Check file has valid GLB magic bytes.

        GLB files start with:
        - Bytes 0-3: 0x46546C67 ('glTF' in ASCII, little-endian)
        - Bytes 4-7: Version number (typically 2)
        - Bytes 8-11: Total file length

        Args:
            path: Path object to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(path, 'rb') as f:
                # Read first 12 bytes (GLB header)
                header = f.read(12)

                if len(header) < self.MIN_GLB_SIZE:
                    return False, (
                        f"File too small to be a valid GLB "
                        f"({len(header)} bytes, minimum {self.MIN_GLB_SIZE} bytes)"
                    )

                # Unpack header: 3 unsigned integers (little-endian)
                try:
                    magic, version, length = struct.unpack('<III', header)
                except struct.error as e:
                    return False, f"Invalid GLB header format: {str(e)}"

                # Check magic bytes
                if magic != self.GLB_MAGIC:
                    return False, (
                        f"Not a valid GLB file (invalid magic bytes). "
                        f"Expected 0x{self.GLB_MAGIC:08X}, got 0x{magic:08X}. "
                        f"Make sure the file is in GLB format, not GLTF or other formats."
                    )

                # Check version (informational warning, not a hard error)
                if version != 2:
                    logger.warning(
                        f"GLB version {version} detected. "
                        f"Expected version 2. File may not load correctly."
                    )

                # Verify length matches actual file size
                actual_size = path.stat().st_size
                if length != actual_size:
                    logger.warning(
                        f"GLB header length ({length} bytes) doesn't match "
                        f"actual file size ({actual_size} bytes). "
                        f"File may be corrupted."
                    )

                logger.debug(
                    f"GLB format valid: version={version}, length={length}"
                )
                return True, ""

        except Exception as e:
            return False, f"Error reading GLB file: {str(e)}"

    def get_file_info(self, file_path: str) -> dict:
        """
        Get detailed information about a GLB file.

        Args:
            file_path: Path to the GLB file

        Returns:
            Dictionary with file information, or error info if invalid

        Example:
            >>> validator = GLBValidator()
            >>> info = validator.get_file_info('models/burger.glb')
            >>> print(f"Size: {info['size_mb']}MB, Version: {info['version']}")
        """
        path = Path(file_path)
        info = {
            'path': str(path.absolute()),
            'name': path.name,
            'exists': path.exists(),
            'is_valid': False,
        }

        if not path.exists():
            info['error'] = 'File not found'
            return info

        try:
            # Get file size
            size_bytes = path.stat().st_size
            info['size_bytes'] = size_bytes
            info['size_mb'] = round(size_bytes / (1024 * 1024), 2)
            info['size_kb'] = round(size_bytes / 1024, 2)

            # Read GLB header
            with open(path, 'rb') as f:
                header = f.read(12)
                if len(header) >= 12:
                    magic, version, length = struct.unpack('<III', header)
                    info['magic'] = f"0x{magic:08X}"
                    info['version'] = version
                    info['header_length'] = length

            # Run validation
            is_valid, error = self.validate(file_path)
            info['is_valid'] = is_valid
            if error:
                info['error'] = error

        except Exception as e:
            info['error'] = str(e)

        return info


def main():
    """
    CLI interface for GLB validator.

    Usage:
        python validate_glb.py <file_path>
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_glb.py <file_path>")
        print("\nExample:")
        print("  python validate_glb.py models/burger.glb")
        sys.exit(1)

    file_path = sys.argv[1]
    validator = GLBValidator()

    print(f"\nValidating: {file_path}")
    print("-" * 60)

    # Get detailed info
    info = validator.get_file_info(file_path)

    print(f"File: {info['name']}")
    print(f"Path: {info['path']}")

    if not info['exists']:
        print(f"❌ ERROR: {info.get('error', 'File not found')}")
        sys.exit(1)

    print(f"Size: {info.get('size_mb', 0)}MB ({info.get('size_kb', 0)}KB)")

    if 'magic' in info:
        print(f"Magic: {info['magic']}")
        print(f"Version: {info['version']}")
        print(f"Header Length: {info['header_length']} bytes")

    print("-" * 60)

    if info['is_valid']:
        print("✅ VALID GLB FILE")
        print("\nThis file is ready for upload!")
        sys.exit(0)
    else:
        print(f"❌ INVALID GLB FILE")
        print(f"\nError: {info.get('error', 'Unknown error')}")
        print("\nFix suggestions:")
        print("  - Ensure the file is in GLB format (not GLTF)")
        print("  - Try re-exporting from Blender/3D software")
        print("  - Use online GLB validators to check file integrity")
        sys.exit(1)


if __name__ == '__main__':
    # Configure logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    main()
