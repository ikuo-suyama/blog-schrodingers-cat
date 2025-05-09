#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import urllib.parse
from pathlib import Path

PORT = 8080

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Translate path to serve files from local_html and assets directories"""
        # Parse the URL and remove query parameters
        parsed_url = urllib.parse.urlparse(path)
        clean_path = parsed_url.path
        
        # Call the original method with the clean path
        translated_path = super().translate_path(clean_path)
        
        # Get the relative path
        rel_path = os.path.relpath(translated_path, os.getcwd())
        
        # If it starts with local_html or assets, serve directly
        if rel_path.startswith(('local_html/', 'assets/')):
            return translated_path
        elif rel_path == '.':
            # For root, redirect to local_html
            return os.path.join(os.getcwd(), 'local_html')
        else:
            # Try to find the file in local_html first, then in assets
            local_html_path = os.path.join(os.getcwd(), 'local_html', rel_path)
            if os.path.exists(local_html_path):
                return local_html_path
            
            # Try to find the file in assets using the path without query parameters
            assets_path = os.path.join(os.getcwd(), 'assets', rel_path)
            if os.path.exists(assets_path):
                return assets_path
            
            # Check if there's a file in assets directory with a similar name (ignoring query params)
            assets_dir = os.path.dirname(assets_path)
            if os.path.exists(assets_dir):
                filename = os.path.basename(rel_path)
                # Remove query params from filename if any
                if '?' in filename:
                    filename = filename.split('?')[0]
                
                # Check if file exists in the directory
                for file in os.listdir(assets_dir):
                    if file.startswith(filename):
                        return os.path.join(assets_dir, file)
                
            return translated_path

def run_server(port=PORT):
    handler = MyHttpRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        print("Serving files from local_html/ and assets/ directories")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            httpd.server_close()

if __name__ == "__main__":
    # Allow port to be passed as an argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    else:
        port = PORT
        
    run_server(port) 