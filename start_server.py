"""
Simple HTTP server for local AR viewer testing.

Usage:
    python start_server.py

Then open in browser:
    http://localhost:8000/ar_viewer/?model=BURGER_001
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

# Configuration
PORT = int(os.environ.get("PORT", 7860))
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types for GLB files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Add CORS headers for local testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

        # Set correct MIME type for GLB files
        if self.path.endswith('.glb'):
            self.send_header('Content-Type', 'model/gltf-binary')

        super().end_headers()


def main():
    """Start the local web server."""
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("AR VIEWER - LOCAL SERVER")
        print("=" * 60)
        print(f"\nServer running at: http://localhost:{PORT}")
        print(f"\nAR Viewer URL: http://localhost:{PORT}/ar_viewer/")
        print("\nExample URLs:")
        print(f"  - http://localhost:{PORT}/ar_viewer/?model=BURGER_001")
        print(f"  - http://localhost:{PORT}/ar_viewer/?model=PIZZA_001")
        print(f"\n(Port read from PORT env var, defaulting to {PORT})")
        print("\nIMPORTANT:")
        print("  1. Update Supabase credentials in ar_viewer/fetch_models.js")
        print("  2. Upload models first using scripts/upload_model.py")
        print("  3. For mobile testing, use ngrok or deploy to Vercel")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        print()

        # Try to open browser automatically
        try:
            webbrowser.open(f"http://localhost:{PORT}/ar_viewer/")
        except Exception:
            pass

        # Start server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")


if __name__ == '__main__':
    main()
