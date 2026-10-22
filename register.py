import http.server
import socketserver
import os
from dotenv import load_dotenv
import urllib.parse
import json
import tempfile
import shutil
from datetime import datetime
import io
import email.parser
import mimetypes
import psycopg2
from psycopg2 import sql, extras
import bcrypt
import re

PORT = 8002
UPLOAD_DIR = 'uploads'
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===================================================================
# DATABASE CONFIGURATION
# ===================================================================

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# ===================================================================
# DATABASE CONNECTION
# ===================================================================

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# ===================================================================
# CREATE TABLE IF NOT EXISTS
# ===================================================================

def create_table():
    """Create the register table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS register (
                id BIGSERIAL NOT NULL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                date_of_birth DATE NOT NULL,
                country VARCHAR(100) NOT NULL,
                province VARCHAR(100) NOT NULL,
                city VARCHAR(100) NOT NULL,
                street_address VARCHAR(255),
                current_activity VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                phone VARCHAR(20) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'register' created/verified successfully")
        return True
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        if conn:
            conn.close()
        return False

# ===================================================================
# VALIDATION FUNCTIONS
# ===================================================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password (min 8 characters)"""
    return len(password) >= 8

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
    
    def process_registration_json(self, json_data, filename):
        """Process the registration JSON and save to database"""
        try:
            # Extract fields from JSON
            first_name = json_data.get('firstName', '').strip()
            last_name = json_data.get('lastName', '').strip()
            dob = json_data.get('dob', '')
            country = json_data.get('country', '').strip()
            province = json_data.get('province', '').strip()
            city = json_data.get('city', '').strip()
            street = json_data.get('street', '').strip()
            activity = json_data.get('activity', '').strip()
            email = json_data.get('email', '').strip()
            phone = json_data.get('phone', '').strip()
            password = json_data.get('password', '')
            
            # Validate required fields
            if not all([first_name, last_name, dob, country, province, city, activity, email, phone, password]):
                return {
                    'success': False,
                    'message': 'Missing required fields in JSON'
                }
            
            # Validate email
            if not validate_email(email):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Validate password
            if not validate_password(password):
                return {
                    'success': False,
                    'message': 'Password must be at least 8 characters'
                }
            
            # Hash the password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Insert into database
            conn = get_db_connection()
            if not conn:
                return {
                    'success': False,
                    'message': 'Database connection failed'
                }
            
            try:
                cur = conn.cursor()
                
                # Check if email already exists
                cur.execute("SELECT id FROM register WHERE email = %s", (email,))
                if cur.fetchone():
                    cur.close()
                    conn.close()
                    return {
                        'success': False,
                        'message': 'Email already registered'
                    }
                
                # Insert new user
                cur.execute("""
                    INSERT INTO register (
                        first_name, last_name, date_of_birth, country,
                        province, city, street_address, current_activity,
                        email, phone, password_hash
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    first_name, last_name, dob, country,
                    province, city, street, activity,
                    email, phone, password_hash
                ))
                
                user_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                
                # Move the JSON file to a processed folder
                processed_dir = os.path.join(UPLOAD_DIR, 'processed')
                os.makedirs(processed_dir, exist_ok=True)
                try:
                    shutil.move(
                        os.path.join(UPLOAD_DIR, filename),
                        os.path.join(processed_dir, filename)
                    )
                except:
                    pass
                
                return {
                    'success': True,
                    'message': 'Registration successful!',
                    'user_id': user_id
                }
                
            except psycopg2.IntegrityError as e:
                if 'email' in str(e):
                    return {
                        'success': False,
                        'message': 'Email already registered'
                    }
                return {
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }
            except psycopg2.Error as e:
                return {
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing registration: {str(e)}'
            }
    
    def handle_login(self):
        """Handle user login with full user data"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'No data provided'
                }).encode())
                return
            
            # Read body
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                self.send_response(400)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Email and password are required'
                }).encode())
                return
            
            # Connect to database
            conn = get_db_connection()
            if not conn:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Database connection failed'
                }).encode())
                return
            
            try:
                cur = conn.cursor(cursor_factory=extras.DictCursor)
                
                # Get full user data including all fields - USING created_at
                cur.execute("""
                    SELECT 
                        id, 
                        first_name, 
                        last_name, 
                        email, 
                        phone, 
                        country, 
                        province,
                        city, 
                        street_address,
                        current_activity,
                        date_of_birth,
                        created_at,
                        password_hash
                    FROM register
                    WHERE email = %s
                """, (email,))
                
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if not user:
                    self.send_response(401)
                    self.send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': 'Invalid email or password'
                    }).encode())
                    return
                
                # Verify password
                password_hash = user['password_hash']
                if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    self.send_response(401)
                    self.send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': 'Invalid email or password'
                    }).encode())
                    return
                
                # Build full name
                full_name = f"{user['first_name']} {user['last_name']}"
                
                # Generate username from first and last name
                username = f"{user['first_name'].lower()}{user['last_name'].lower()}"
                # Remove any spaces or special characters
                username = re.sub(r'[^a-zA-Z0-9]', '', username)
                
                # Build bio
                if user['current_activity']:
                    bio = f"Student at LogicTree Academy · Learning {user['current_activity']}"
                else:
                    bio = "Student at LogicTree Academy"
                
                # Login successful - return all user data (without password)
                user_data = {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'name': full_name,
                    'email': user['email'],
                    'phone': user['phone'] or '',
                    'country': user['country'] or '',
                    'province': user['province'] or '',
                    'city': user['city'] or '',
                    'street_address': user['street_address'] or '',
                    'current_activity': user['current_activity'] or '',
                    'date_of_birth': user['date_of_birth'].isoformat() if user['date_of_birth'] else '',
                    'created_at': user['created_at'].isoformat() if user['created_at'] else '',
                    'username': username,
                    'bio': bio
                }
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': 'Login successful',
                    'user': user_data
                }).encode())
                
                print(f"✅ User logged in: {full_name} ({email})")
                print(f"   User data returned: {json.dumps(user_data, indent=2)}")
                
            except psycopg2.Error as e:
                print(f"Database error during login: {e}")
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }).encode())
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_response(400)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'Invalid JSON data'
            }).encode())
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'Server error: {str(e)}'
            }).encode())
    
    def handle_get_user(self, user_id):
        """Get user data by ID"""
        try:
            conn = get_db_connection()
            if not conn:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Database connection failed'
                }).encode())
                return
            
            try:
                cur = conn.cursor(cursor_factory=extras.DictCursor)
                cur.execute("""
                    SELECT 
                        id, first_name, last_name, email, phone, 
                        country, province, city, street_address,
                        current_activity, date_of_birth, created_at
                    FROM register
                    WHERE id = %s
                """, (user_id,))
                
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if not user:
                    self.send_response(404)
                    self.send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': 'User not found'
                    }).encode())
                    return
                
                # Build full name
                full_name = f"{user['first_name']} {user['last_name']}"
                
                # Generate username
                username = f"{user['first_name'].lower()}{user['last_name'].lower()}"
                username = re.sub(r'[^a-zA-Z0-9]', '', username)
                
                user_data = {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'name': full_name,
                    'email': user['email'],
                    'phone': user['phone'] or '',
                    'country': user['country'] or '',
                    'province': user['province'] or '',
                    'city': user['city'] or '',
                    'street_address': user['street_address'] or '',
                    'current_activity': user['current_activity'] or '',
                    'date_of_birth': user['date_of_birth'].isoformat() if user['date_of_birth'] else '',
                    'created_at': user['created_at'].isoformat() if user['created_at'] else '',
                    'username': username,
                    'bio': f"Student at LogicTree Academy · Learning {user['current_activity']}" if user['current_activity'] else "Student at LogicTree Academy"
                }
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'user': user_data
                }).encode())
                
            except psycopg2.Error as e:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'Server error: {str(e)}'
            }).encode())
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Get user by ID endpoint
        if parsed_path.path.startswith('/api/user/'):
            user_id = parsed_path.path.split('/api/user/')[-1]
            try:
                user_id = int(user_id)
                self.handle_get_user(user_id)
            except ValueError:
                self.send_response(400)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Invalid user ID'
                }).encode())
            return
        
        # Get current user from session
        if parsed_path.path == '/api/me':
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'Session not implemented. Use /api/login first.'
            }).encode())
            return
        
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
                self.send_cors_headers()
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                
                print(f"Viewed: {filename}")
            else:
                self.send_response(404)
                self.send_cors_headers()
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
        
        # Health check endpoint
        if parsed_path.path == '/api/health' or parsed_path.path == '/api/health/':
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'server': 'Registration Server',
                'port': PORT
            }).encode())
            return
        
        # Get users endpoint (debug)
        if parsed_path.path == '/api/users' or parsed_path.path == '/api/users/':
            conn = get_db_connection()
            if not conn:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'Database connection failed'}).encode())
                return
            
            try:
                cur = conn.cursor(cursor_factory=extras.DictCursor)
                cur.execute("""
                    SELECT id, first_name, last_name, email, phone, 
                           country, city, current_activity, created_at
                    FROM register
                    ORDER BY created_at DESC
                """)
                users = cur.fetchall()
                cur.close()
                conn.close()
                
                # Convert to list of dicts
                user_list = []
                for user in users:
                    user_list.append({
                        'id': user['id'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'name': f"{user['first_name']} {user['last_name']}",
                        'email': user['email'],
                        'phone': user['phone'],
                        'country': user['country'],
                        'city': user['city'],
                        'current_activity': user['current_activity'],
                        'created_at': user['created_at'].isoformat() if user['created_at'] else ''
                    })
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'users': user_list
                }).encode())
            except psycopg2.Error as e:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode())
            return
        
        # Default - show upload form
        self.serve_upload_form()
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Login endpoint
        if parsed_path.path == '/api/login' or parsed_path.path == '/api/login/':
            self.handle_login()
            return
        
        # File upload endpoint (also handles registration JSON)
        if parsed_path.path == '/upload' or parsed_path.path == '/upload/':
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
                
                # Check if it's a JSON file (registration data)
                is_registration = filename.endswith('.json') and 'registration' in filename.lower()
                
                # Save file
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                
                file_size = os.path.getsize(filepath)
                print(f"Uploaded: {filename} ({file_size} bytes)")
                
                # If it's a registration JSON, process it
                if is_registration:
                    try:
                        # Parse the JSON
                        with open(filepath, 'r') as f:
                            json_data = json.load(f)
                        
                        # Process registration
                        result = self.process_registration_json(json_data, filename)
                        
                        if result['success']:
                            self.send_response(201)
                            self.send_cors_headers()
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                'success': True,
                                'message': result['message'],
                                'user_id': result.get('user_id')
                            }).encode())
                            print(f"✅ Registration processed for: {json_data.get('email')}")
                        else:
                            self.send_response(400)
                            self.send_cors_headers()
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                'success': False,
                                'message': result['message']
                            }).encode())
                            print(f"❌ Registration failed: {result['message']}")
                    except json.JSONDecodeError as e:
                        self.send_response(400)
                        self.send_cors_headers()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': False,
                            'message': f'Invalid JSON file: {str(e)}'
                        }).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_cors_headers()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': False,
                            'message': f'Error processing registration: {str(e)}'
                        }).encode())
                else:
                    # Regular file upload response
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
                .endpoint-info {{ background: #e8f5e9; padding: 12px; border-radius: 8px; margin-top: 10px; }}
                .endpoint-info code {{ background: #c8e6c9; padding: 2px 6px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h2>📤 Registration Server</h2>
            
            <div class="endpoint-info">
                <strong>📋 Available Endpoints:</strong><br>
                <code>POST /api/login</code> - User login (returns full user data)<br>
                <code>GET /api/user/&lt;id&gt;</code> - Get user by ID<br>
                <code>POST /upload</code> - Upload registration JSON (auto-processed to database)<br>
                <code>GET /list</code> - List uploaded files<br>
                <code>GET /download/&lt;filename&gt;</code> - Download file<br>
                <code>GET /view/&lt;filename&gt;</code> - View file in browser<br>
                <code>GET /delete/&lt;filename&gt;</code> - Delete file<br>
                <code>GET /api/health</code> - Health check<br>
                <code>GET /api/users</code> - List registered users
            </div>
            
            <div class="upload-form">
                <h3>📤 Upload Registration JSON</h3>
                <p style="color: #666;">Upload a registration JSON file to automatically process it into the database.</p>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".json" required>
                    <input type="submit" value="Upload & Process">
                </form>
            </div>
            
            {file_list_html}
            
            <div class="info">
                <p><strong>Server:</strong> http://localhost:{PORT}</p>
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
    # Create table on startup
    create_table()
    
    try:
        with ThreadedHTTPServer(("0.0.0.0", PORT), FileServerHandler) as httpd:
            print("=" * 60)
            print(f"🚀 LogicTree Registration Server Started Successfully!")
            print("=" * 60)
            print(f"📡 Listening on: http://0.0.0.0:{PORT}")
            print(f"🌐 Access from: http://localhost:{PORT}")
            print(f"🌍 Access from network: http://YOUR_IP:{PORT}")
            print("=" * 60)
            print("📋 Available Endpoints:")
            print("   POST /api/login     - User login (returns full user data)")
            print("   GET  /api/user/:id  - Get user data by ID")
            print("   POST /upload       - Upload registration JSON → auto-process to DB")
            print("   GET  /list         - List files")
            print("   GET  /download/*   - Download file")
            print("   GET  /view/*       - View file")
            print("   GET  /delete/*     - Delete file")
            print("   GET  /api/health   - Health check")
            print("   GET  /api/users    - List registered users")
            print("=" * 60)
            print("✅ CORS headers enabled for ALL endpoints")
            print("✅ Database: PostgreSQL connected")
            print("✅ Auto-process: JSON files with 'registration' in name are auto-imported")
            print("✅ Login: Email + password authentication with bcrypt")
            print("✅ Returns full user data: name, email, phone, address, etc.")
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