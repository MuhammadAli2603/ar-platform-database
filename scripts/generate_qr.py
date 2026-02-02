"""
QR Code Generator for AR Platform.

Generates QR codes that link to AR viewer URLs for 3D models.

Features:
- High error correction (Level H - 30%)
- 1000x1000px resolution (print quality)
- Optional logo/branding in center
- Batch generation support
- Customizable colors

Usage:
    # Single QR code
    python generate_qr.py BURGER_001

    # Batch QR codes
    python generate_qr.py BURGER_001 PIZZA_001 COFFEE_001

    # With custom settings
    python generate_qr.py BURGER_001 --size 2000 --output qr_codes/custom/
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class QRGenerator:
    """
    Generate QR codes for AR model viewing.

    Attributes:
        base_url: Base URL for AR viewer
        output_dir: Directory where QR codes will be saved
        size: QR code image size in pixels
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        output_dir: str = 'qr_codes',
        size: int = 1000
    ):
        """
        Initialize QR code generator.

        Args:
            base_url: Base URL for AR viewer (defaults to Config.BASE_AR_VIEWER_URL)
            output_dir: Directory to save QR codes
            size: QR code size in pixels (default: 1000x1000)
        """
        self.base_url = base_url or Config.BASE_AR_VIEWER_URL
        self.output_dir = Path(output_dir)
        self.size = size

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"QRGenerator initialized (base_url: {self.base_url})")

    def generate(
        self,
        model_id: str,
        save_path: Optional[str] = None,
        add_label: bool = True,
        fill_color: str = "black",
        back_color: str = "white"
    ) -> str:
        """
        Generate QR code for a model.

        Args:
            model_id: The model ID (e.g., 'BURGER_001')
            save_path: Optional custom save path
            add_label: Whether to add model ID label below QR code
            fill_color: QR code foreground color
            back_color: QR code background color

        Returns:
            Path to saved QR code image

        Example:
            >>> gen = QRGenerator()
            >>> qr_path = gen.generate('BURGER_001')
            >>> print(f"QR code saved to: {qr_path}")
        """
        logger.info(f"Generating QR code for model: {model_id}")

        # Build AR viewer URL
        url = f"{self.base_url}?model={model_id}"
        logger.debug(f"QR code URL: {url}")

        # Create QR code
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust size
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% error correction
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Generate image with rounded corners (modern style)
        try:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                fill_color=fill_color,
                back_color=back_color
            )
        except Exception:
            # Fallback to basic image if styled image fails
            logger.warning("Styled QR code failed, using basic QR code")
            img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Resize to desired size
        img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)

        # Add label if requested
        if add_label:
            img = self._add_label(img, model_id)

        # Determine save path
        if not save_path:
            save_path = self.output_dir / f"{model_id}_qr.png"
        else:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save image
        img.save(save_path, "PNG", dpi=(300, 300))
        logger.info(f"✅ QR code saved: {save_path}")

        return str(save_path)

    def _add_label(self, img: Image.Image, label_text: str) -> Image.Image:
        """
        Add a text label below the QR code.

        Args:
            img: QR code image
            label_text: Text to add

        Returns:
            Image with label
        """
        # Create new image with extra height for label
        label_height = 80
        new_img = Image.new(
            'RGB',
            (img.width, img.height + label_height),
            color='white'
        )

        # Paste QR code at top
        new_img.paste(img, (0, 0))

        # Draw label
        draw = ImageDraw.Draw(new_img)

        # Try to use a better font, fallback to default
        try:
            # Adjust font size based on image width
            font_size = int(self.size / 25)
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            logger.debug("Custom font not available, using default")
            font = ImageFont.load_default()

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (new_img.width - text_width) // 2
        text_y = img.height + (label_height - text_height) // 2

        # Draw text
        draw.text(
            (text_x, text_y),
            label_text,
            fill='black',
            font=font
        )

        return new_img

    def generate_batch(
        self,
        model_ids: List[str],
        add_label: bool = True
    ) -> List[str]:
        """
        Generate QR codes for multiple models.

        Args:
            model_ids: List of model IDs
            add_label: Whether to add labels

        Returns:
            List of paths to generated QR codes
        """
        logger.info(f"Generating {len(model_ids)} QR codes...")

        paths = []
        for model_id in model_ids:
            try:
                path = self.generate(model_id, add_label=add_label)
                paths.append(path)
            except Exception as e:
                logger.error(f"Failed to generate QR for {model_id}: {e}")

        logger.info(f"✅ Generated {len(paths)}/{len(model_ids)} QR codes")
        return paths


def main():
    """CLI interface for QR code generator."""
    parser = argparse.ArgumentParser(
        description='Generate QR codes for AR model viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single QR code
  python generate_qr.py BURGER_001

  # Generate multiple QR codes
  python generate_qr.py BURGER_001 PIZZA_001 COFFEE_001

  # Custom size and output directory
  python generate_qr.py BURGER_001 --size 2000 --output qr_codes/high_res/

  # No label
  python generate_qr.py BURGER_001 --no-label

  # Custom colors (brand colors)
  python generate_qr.py BURGER_001 --fill-color "#FF5733" --back-color "#FFFFFF"
        """
    )

    parser.add_argument(
        'model_ids',
        nargs='+',
        help='Model IDs to generate QR codes for'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='qr_codes',
        help='Output directory (default: qr_codes/)'
    )
    parser.add_argument(
        '--size',
        '-s',
        type=int,
        default=1000,
        help='QR code size in pixels (default: 1000)'
    )
    parser.add_argument(
        '--no-label',
        action='store_true',
        help='Do not add model ID label'
    )
    parser.add_argument(
        '--fill-color',
        default='black',
        help='QR code foreground color (default: black)'
    )
    parser.add_argument(
        '--back-color',
        default='white',
        help='QR code background color (default: white)'
    )
    parser.add_argument(
        '--base-url',
        help=f'Custom base URL (default: {Config.BASE_AR_VIEWER_URL})'
    )

    args = parser.parse_args()

    # Create generator
    generator = QRGenerator(
        base_url=args.base_url,
        output_dir=args.output,
        size=args.size
    )

    print(f"\nGenerating QR codes for {len(args.model_ids)} model(s)...")
    print(f"Output directory: {args.output}")
    print(f"Size: {args.size}x{args.size}px")
    print(f"Base URL: {generator.base_url}")
    print()

    # Generate QR codes
    if len(args.model_ids) == 1:
        # Single QR code
        path = generator.generate(
            args.model_ids[0],
            add_label=not args.no_label,
            fill_color=args.fill_color,
            back_color=args.back_color
        )
        print(f"✅ QR code generated: {path}")
        print(f"\nAR Viewer URL: {generator.base_url}?model={args.model_ids[0]}")
        print("\nNext steps:")
        print("  1. Print the QR code or display on screen")
        print("  2. Scan with mobile device")
        print("  3. AR viewer should open automatically")

    else:
        # Batch generation
        paths = []
        for model_id in args.model_ids:
            try:
                path = generator.generate(
                    model_id,
                    add_label=not args.no_label,
                    fill_color=args.fill_color,
                    back_color=args.back_color
                )
                paths.append(path)
                print(f"✅ {model_id} -> {path}")
            except Exception as e:
                print(f"❌ {model_id} -> Error: {e}")

        print(f"\n✅ Generated {len(paths)}/{len(args.model_ids)} QR codes")
        print(f"All QR codes saved to: {args.output}/")

    sys.exit(0)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    main()
