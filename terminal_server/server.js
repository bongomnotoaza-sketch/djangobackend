import { WebSocketServer } from 'ws';
import { spawn } from 'node-pty';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import express from 'express';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- Configuration ---
const WS_PORT = 3000;  // WebSocket port
const HTTP_PORT = 8080; // HTTP server port for serving HTML
const HOST = '0.0.0.0'; // Listen on all network interfaces

// --- WebSocket Server (for terminal communication) ---
const wss = new WebSocketServer({ port: WS_PORT, host: HOST });
console.log(`🔌 WebSocket server running on ws://${HOST}:${WS_PORT}`);

wss.on('connection', (ws, req) => {
    console.log('📱 Client connected');

    // Spawn a bash shell with minimal prompt
    const shell = spawn('/bin/bash', [], {
        name: 'xterm-256color',
        cols: 80,
        rows: 30,
        cwd: process.env.HOME,
        env: { ...process.env, PS1: '$ ' }  // Clean, minimal prompt
    });

    // Forward shell output to WebSocket client
    shell.onData((data) => {
        ws.send(data);
    });

    // Forward WebSocket messages to shell — except resize control
    // frames, which are prefixed with \x01 and update the pty size
    // instead of being typed into the shell.
    ws.on('message', (data) => {
        const str = data.toString();

        if (str.charCodeAt(0) === 1) {
            try {
                const { cols, rows } = JSON.parse(str.slice(1));
                if (cols > 0 && rows > 0) {
                    shell.resize(cols, rows);
                }
            } catch (err) {
                // malformed resize payload, ignore
            }
            return;
        }

        shell.write(str);
    });

    // Handle WebSocket close
    ws.on('close', () => {
        console.log('📱 Client disconnected');
        shell.kill();
    });

    // Handle shell exit
    shell.onExit(() => {
        ws.close();
    });

    // No injected banner — the shell's own prompt is the only
    // thing that ever gets written to the client.
});

// --- HTTP Server (to serve your HTML page) ---
const app = express();

// Serve static files from the current directory
app.use(express.static(__dirname));

// Or if you want to keep HTML in a separate folder:
// app.use(express.static(path.join(__dirname, 'public')));

app.listen(HTTP_PORT, HOST, () => {
    console.log(`🌐 HTTP server running on http://${HOST}:${HTTP_PORT}`);
});

console.log(`📝 To test: open http://localhost:${HTTP_PORT} in your browser`);
console.log(`🔗 WebSocket: ws://localhost:${WS_PORT}`);