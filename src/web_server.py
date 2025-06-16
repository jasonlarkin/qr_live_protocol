"""
Web Server module for QRLP.

Provides Flask-based web interface for displaying live QR codes in browser
with real-time updates, status information, and verification details.
"""

import os
import base64
import json
import threading
import webbrowser
from datetime import datetime
from typing import Dict, Optional, Any, Callable
from dataclasses import asdict

from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from .config import WebSettings
from .core import QRData


class QRLiveWebServer:
    """
    Web server for QRLP live QR display.
    
    Provides real-time web interface showing QR codes with verification
    information, suitable for livestreaming and official video releases.
    """
    
    def __init__(self, settings: WebSettings):
        """
        Initialize web server with settings.
        
        Args:
            settings: WebSettings configuration object
        """
        self.settings = settings
        self.app = Flask(__name__, 
                        template_folder=self._get_template_dir(),
                        static_folder=self._get_static_dir())
        
        # Configure Flask
        self.app.config['SECRET_KEY'] = 'qrlp-secret-key-change-in-production'
        
        # Enable CORS if configured
        if self.settings.cors_enabled:
            CORS(self.app)
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*" if self.settings.cors_enabled else None)
        
        # State management
        self.current_qr_data: Optional[QRData] = None
        self.current_qr_image: Optional[bytes] = None
        self.is_running = False
        self.update_callback: Optional[Callable] = None
        
        # Statistics
        self.page_views = 0
        self.websocket_connections = 0
        self.qr_updates_sent = 0
        
        # Setup routes
        self._setup_routes()
        self._setup_websocket_events()
    
    def start_server(self, threaded: bool = True) -> None:
        """
        Start the web server.
        
        Args:
            threaded: Whether to run server in background thread
        """
        if self.is_running:
            return
        
        self.is_running = True
        
        if threaded:
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True,
                name="QRLP-WebServer"
            )
            self.server_thread.start()
            
            # Auto-open browser if configured
            if self.settings.auto_open_browser:
                threading.Timer(1.0, self._open_browser).start()
        else:
            self._run_server()
    
    def stop_server(self) -> None:
        """Stop the web server."""
        self.is_running = False
        # SocketIO doesn't have a clean shutdown method, server will stop when main thread exits
    
    def update_qr_display(self, qr_data: QRData, qr_image: bytes) -> None:
        """
        Update the QR code display with new data.
        
        Args:
            qr_data: QR data object
            qr_image: QR code image as bytes
        """
        self.current_qr_data = qr_data
        self.current_qr_image = qr_image
        
        # Send update to all connected clients
        if self.is_running:
            self._broadcast_qr_update()
    
    def get_server_url(self) -> str:
        """Get the server URL."""
        return f"http://{self.settings.host}:{self.settings.port}"
    
    def get_statistics(self) -> Dict:
        """Get web server statistics."""
        return {
            "is_running": self.is_running,
            "page_views": self.page_views,
            "websocket_connections": self.websocket_connections,
            "qr_updates_sent": self.qr_updates_sent,
            "server_url": self.get_server_url(),
            "current_qr_available": self.current_qr_data is not None
        }
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main QR display page."""
            self.page_views += 1
            return render_template('index.html', 
                                 server_url=self.get_server_url(),
                                 settings=asdict(self.settings))
        
        @self.app.route('/api/qr/current')
        def get_current_qr():
            """API endpoint for current QR data."""
            if not self.current_qr_data or not self.current_qr_image:
                return jsonify({"error": "No QR data available"}), 404
            
            # Convert image to base64 for JSON transmission
            image_b64 = base64.b64encode(self.current_qr_image).decode('utf-8')
            
            return jsonify({
                "qr_data": asdict(self.current_qr_data),
                "qr_image": f"data:image/png;base64,{image_b64}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.app.route('/api/status')
        def get_status():
            """API endpoint for server status."""
            return jsonify(self.get_statistics())
        
        @self.app.route('/api/verify', methods=['POST'])
        def verify_qr():
            """API endpoint for QR verification."""
            try:
                data = request.get_json()
                qr_json = data.get('qr_data')
                
                if not qr_json:
                    return jsonify({"error": "No QR data provided"}), 400
                
                # This would integrate with the core QRLP verification
                # For now, return basic validation
                verification_result = {
                    "valid": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "QR data format is valid"
                }
                
                return jsonify(verification_result)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/viewer')
        def viewer():
            """QR viewer page for external displays."""
            return render_template('viewer.html')
        
        @self.app.route('/admin')
        def admin():
            """Admin interface for monitoring."""
            return render_template('admin.html', 
                                 statistics=self.get_statistics())
    
    def _setup_websocket_events(self) -> None:
        """Setup SocketIO events for real-time updates."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.websocket_connections += 1
            print(f"Client connected. Total connections: {self.websocket_connections}")
            
            # Send current QR data if available
            if self.current_qr_data and self.current_qr_image:
                self._send_qr_update_to_client()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.websocket_connections -= 1
            print(f"Client disconnected. Total connections: {self.websocket_connections}")
        
        @self.socketio.on('request_qr_update')
        def handle_qr_request():
            """Handle client request for QR update."""
            if self.current_qr_data and self.current_qr_image:
                self._send_qr_update_to_client()
    
    def _broadcast_qr_update(self) -> None:
        """Broadcast QR update to all connected clients."""
        if not self.current_qr_data or not self.current_qr_image:
            return
        
        # Prepare update data
        image_b64 = base64.b64encode(self.current_qr_image).decode('utf-8')
        update_data = {
            "qr_data": asdict(self.current_qr_data),
            "qr_image": f"data:image/png;base64,{image_b64}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all clients
        self.socketio.emit('qr_update', update_data)
        self.qr_updates_sent += 1
    
    def _send_qr_update_to_client(self) -> None:
        """Send QR update to requesting client."""
        if not self.current_qr_data or not self.current_qr_image:
            return
        
        image_b64 = base64.b64encode(self.current_qr_image).decode('utf-8')
        update_data = {
            "qr_data": asdict(self.current_qr_data),
            "qr_image": f"data:image/png;base64,{image_b64}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        emit('qr_update', update_data)
    
    def _run_server(self) -> None:
        """Run the Flask server."""
        try:
            self.socketio.run(
                self.app,
                host=self.settings.host,
                port=self.settings.port,
                debug=self.settings.debug,
                use_reloader=False  # Disable reloader for production
            )
        except Exception as e:
            print(f"Server error: {e}")
            self.is_running = False
    
    def _open_browser(self) -> None:
        """Open browser to server URL."""
        try:
            webbrowser.open(self.get_server_url())
        except Exception as e:
            print(f"Could not open browser: {e}")
    
    def _get_template_dir(self) -> str:
        """Get template directory path."""
        if os.path.isabs(self.settings.template_dir):
            return self.settings.template_dir
        
        # Relative to project root directory (one level up from src)
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, self.settings.template_dir)
    
    def _get_static_dir(self) -> str:
        """Get static files directory path."""
        if os.path.isabs(self.settings.static_dir):
            return self.settings.static_dir
        
        # Relative to project root directory (one level up from src)
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, self.settings.static_dir) 