import os
import subprocess
import sys
import tempfile
import json

workspace = tempfile.mkdtemp()



env_path = "/home/alikho/Documents/build_env/bin/python"
code = "import random\nimport string\nfrom http.server import HTTPServer, BaseHTTPRequestHandler\nimport json\n\ndef generate_password(length=12, use_special=True):\n    \"\"\"Generate a random password with given length and options.\"\"\"\n    chars = string.ascii_letters + string.digits\n    if use_special:\n        chars += string.punctuation\n    \n    password = []\n    for _ in range(length):\n        password.append(random.choice(chars))\n    \n    return ''.join(password)\n\nclass PasswordHandler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        if self.path == '/':\n            self.send_response(200)\n            self.send_header('Content-type', 'text/html')\n            self.end_headers()\n            \n            html = '''\n            <!DOCTYPE html>\n            <html>\n            <head>\n                <title>Password Generator</title>\n                <style>\n                    body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }\n                    input, button { padding: 10px; margin: 5px 0; }\n                    button { background: #4CAF50; color: white; border: none; cursor: pointer; }\n                    #password { font-size: 20px; font-weight: bold; color: #2E7D32; }\n                </style>\n            </head>\n            <body>\n                <h1>🔐 Password Generator</h1>\n                <label>Length: <input type=\"number\" id=\"length\" value=\"12\" min=\"4\" max=\"64\"></label><br>\n                <label><input type=\"checkbox\" id=\"special\" checked> Include special characters</label><br>\n                <button onclick=\"generate()\">Generate Password</button>\n                <div id=\"password\" style=\"margin-top:20px;padding:15px;background:#f0f0f0;border-radius:5px;\"></div>\n                \n                <script>\n                    async function generate() {\n                        const length = document.getElementById('length').value;\n                        const special = document.getElementById('special').checked;\n                        \n                        const response = await fetch('/generate', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({ length: parseInt(length), special: special })\n                        });\n                        \n                        const data = await response.json();\n                        document.getElementById('password').textContent = data.password;\n                    }\n                </script>\n            </body>\n            </html>\n            '''\n            self.wfile.write(html.encode())\n        else:\n            self.send_response(404)\n            self.end_headers()\n    \n    def do_POST(self):\n        if self.path == '/generate':\n            content_length = int(self.headers['Content-Length'])\n            post_data = self.rfile.read(content_length)\n            data = json.loads(post_data)\n            \n            length = data.get('length', 12)\n            special = data.get('special', True)\n            \n            password = generate_password(length, special)\n            \n            self.send_response(200)\n            self.send_header('Content-type', 'application/json')\n            self.end_headers()\n            \n            response = json.dumps({'password': password})\n            self.wfile.write(response.encode())\n        else:\n            self.send_response(404)\n            self.end_headers()\n\ndef main():\n    port = 8000\n    server = HTTPServer(('localhost', port), PasswordHandler)\n    print(f\"Server running at http://localhost:{port}\")\n    print(\"Press Ctrl+C to stop\")\n    server.serve_forever()\n\nif __name__ == \"__main__\":\n    main()"
npm_path = "/home/alikho/Documents/final/logictree/dashboard/my-web-console"
port = ""

def python_run():
    
    path = os.path.join(workspace,"file.py")
    with open(path,"w") as file:
        file.write(code)
        
    subprocess.run([env_path,path])
    
def node_run():
    
    path = os.path.join(workspace,"file.js")
    with open(path,"w") as file:
        file.write(code)
        
    subprocess.run(["node",path],cwd = npm_path
                   )
    
python_run()
    

        
    
    
    