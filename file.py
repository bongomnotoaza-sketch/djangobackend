import http.server
import socketserver
import os
import urllib.parse
import json
import tempfile
import shutil
from datetime import datetime
import io
import email.parser
import mimetypes

PORT = 6060
UPLOAD_DIR = 'uploads'
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileServerHandler(http.server.SimpleHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Override to add timestamps to logs"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")
    
    def send_cors_headers(self):
        """Send CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def parse_multipart(self, content_type, body):
        """Parse multipart form data manually"""
        try:
            # Parse the content type header
            boundary = None
            for part in content_type.split(';'):
                part = part.strip()
                if part.startswith('boundary='):
                    boundary = part[9:]
                    if boundary.startswith('"') and boundary.endswith('"'):
                        boundary = boundary[1:-1]
                    break
            
            if not boundary:
                return None, None
            
            # Split the body by boundary
            boundary_bytes = boundary.encode()
            parts = body.split(b'--' + boundary_bytes)
            
            for part in parts:
                if not part or part == b'--\r\n' or part == b'--':
                    continue
                
                # Parse headers and content
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue
                
                headers = part[:header_end].decode()
                content = part[header_end + 4:]
                
                # Remove trailing \r\n
                if content.endswith(b'\r\n'):
                    content = content[:-2]
                
                # Check if this is a file field
                if 'filename=' in headers:
                    # Extract filename
                    filename = None
                    for line in headers.split('\r\n'):
                        if 'filename=' in line:
                            start = line.find('filename="') + 10
                            end = line.find('"', start)
                            if start > 9 and end > start:
                                filename = line[start:end]
                                break
                    
                    if filename:
                        filename = os.path.basename(filename)
                        return filename, content
                
                # Check if it's a regular form field (not used in our case)
                if 'name="file"' in headers:
                    return None, None
            
            return None, None
        except Exception as e:
            print(f"Error parsing multipart: {e}")
            return None, None
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Download file (forces download)
        if parsed_path.path.startswith('/download/'):
            filename = parsed_path.path.split('/download/')[-1]
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                # Prevent any client/proxy from caching a stale copy of this file
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                
                print(f"Downloaded: {filename}")
            else:
                self.send_error(404, f'File "{filename}" not found')
            return
        
        # View file in browser
        if parsed_path.path.startswith('/view/'):
            filename = parsed_path.path.split('/view/')[-1]
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            if os.path.exists(filepath):
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                
                self.send_response(200)
                self.send_cors_headers()  # <-- FIX: Added CORS headers here
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                
                print(f"Viewed: {filename}")
            else:
                self.send_response(404)
                self.send_cors_headers()  # <-- FIX: Send CORS even for 404
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'File "{filename}" not found'}).encode())
                print(f"File not found: {filename}")
            return
        
        # List files (JSON format)
        if parsed_path.path == '/list' or parsed_path.path == '/list/':
            try:
                files = os.listdir(UPLOAD_DIR)
                file_list = []
                for f in files:
                    filepath = os.path.join(UPLOAD_DIR, f)
                    if os.path.isfile(filepath):
                        file_list.append({
                            'name': f,
                            'size': os.path.getsize(filepath),
                            'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                            'modified': os.path.getmtime(filepath),
                            'modified_str': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                file_list.sort(key=lambda x: x['modified'], reverse=True)
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                self.wfile.write(json.dumps(file_list, indent=2).encode())
                print(f"Listed {len(file_list)} files")
            except Exception as e:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        
        # Delete file
        if parsed_path.path.startswith('/delete/'):
            filename = parsed_path.path.split('/delete/')[-1]
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': f'File "{filename}" deleted successfully',
                    'success': True
                }).encode())
                print(f"Deleted: {filename}")
            else:
                self.send_response(404)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': f'File "{filename}" not found',
                    'success': False
                }).encode())
            return
        
        # Default - show upload form
        self.serve_upload_form()
    
    def do_POST(self):
        if self.path == '/upload' or self.path == '/upload/':
            try:
                # Read the content length
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > MAX_CONTENT_LENGTH:
                    self.send_response(413)
                    self.send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': f'File too large. Max size: {MAX_CONTENT_LENGTH // (1024*1024)}MB'
                    }).encode())
                    return
                
                # Read the body
                body = self.rfile.read(content_length)
                
                # Parse multipart
                content_type = self.headers.get('Content-Type', '')
                filename, file_data = self.parse_multipart(content_type, body)
                
                if not filename or not file_data:
                    self.send_response(400)
                    self.send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'No file uploaded or invalid file data'
                    }).encode())
                    return
                
                # Save file (overwrites if it already exists)
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                # Save file (overwrites if it already exists)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                
                file_size = os.path.getsize(filepath)
                
                # Send success response
                response_data = {
                    'message': 'File uploaded successfully',
                    'filename': filename,
                    'original_name': filename,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'path': filepath
                }
                
                self.send_response(201)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
                
                print(f"Uploaded: {filename} ({file_size} bytes)")
                
            except Exception as e:
                print(f"Upload error: {str(e)}")
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': f'Upload failed: {str(e)}'
                }).encode())
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def serve_upload_form(self):
        """Serve the main upload form with file list"""
        files = []
        try:
            for f in os.listdir(UPLOAD_DIR):
                filepath = os.path.join(UPLOAD_DIR, f)
                if os.path.isfile(filepath):
                    files.append({
                        'name': f,
                        'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                    })
            files.sort(key=lambda x: x['modified'], reverse=True)
        except:
            pass
        
        file_list_html = ''
        if files:
            file_list_html = '<h3>📁 Uploaded Files</h3><ul>'
            for f in files[:20]:
                file_list_html += f'''
                    <li>
                        <strong>{f['name']}</strong> 
                        ({f['size_mb']} MB) 
                        <a href="/download/{f['name']}">⬇️ Download</a>
                        <a href="/view/{f['name']}">👁️ View</a>
                        <a href="/delete/{f['name']}" onclick="return confirm('Delete this file?')">🗑️ Delete</a>
                        <span style="color: #666; font-size: 0.8em;">{f['modified']}</span>
                    </li>
                '''
            file_list_html += '</ul>'
            if len(files) > 20:
                file_list_html += f'<p><a href="/list">View all {len(files)} files (JSON)</a></p>'
        
        html = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h2 {{ color: #333; }}
                .upload-form {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                input[type="file"] {{ padding: 10px; }}
                input[type="submit"] {{ background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
                input[type="submit"]:hover {{ background: #45a049; }}
                ul {{ list-style: none; padding: 0; }}
                li {{ padding: 8px; border-bottom: 1px solid #eee; }}
                li:hover {{ background: #f9f9f9; }}
                a {{ color: #2196F3; text-decoration: none; margin-right: 10px; }}
                a:hover {{ text-decoration: underline; }}
                .info {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h2>📤 File Upload Server</h2>
            
            <div class="upload-form">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" required>
                    <input type="submit" value="Upload File">
                </form>
            </div>
            
            {file_list_html}
            
            <div class="info">
                <p><strong>Server:</strong> {self.server.server_name}:{self.server.server_port}</p>
                <p><strong>Upload directory:</strong> {os.path.abspath(UPLOAD_DIR)}</p>
            </div>
        </body>
        </html>
        '''
        
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

# Create and start the server
class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    try:
        with ThreadedHTTPServer(("0.0.0.0", PORT), FileServerHandler) as httpd:
            print("=" * 60)
            print(f"🚀 File Server Started Successfully!")
            print("=" * 60)
            print(f"📡 Listening on: http://0.0.0.0:{PORT}")
            print(f"🌐 Access from: http://localhost:{PORT}")
            print(f"🌍 Access from network: http://YOUR_IP:{PORT}")
            print(f"📁 Upload directory: {os.path.abspath(UPLOAD_DIR)}")
            print("=" * 60)
            print("✅ CORS headers enabled for ALL endpoints")
            print("✅ Multipart form parsing fixed")
            print("=" * 60)
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()