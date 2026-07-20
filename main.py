# =========================================================
# SENTINEL MOBILE NODE - KIVY PRODUCTION CORE WITH OTA BUILD
# =========================================================
import cv2
import socket
import pickle
import struct
import threading
import urllib.request
import json
import webbrowser
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform

# --- METADATA CONFIGURATION FOR GITHUB OTA ---
# Replace with your actual GitHub username and repository name
GITHUB_API_URL = "https://api.github.com/repos/adithyajaya/sentinel-mobile/releases/latest"
CURRENT_VERSION = "1.0.0"

class SentinelMobileApp(App):
    def build(self):
        # 1. Standard UI Layout Structure
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        self.status_label = Label(
            text="=== SENTINEL MOBILE NODE ===", 
            font_size='20sp', 
            bold=True
        )
        self.info_label = Label(
            text="Initializing System Component Frameworks...", 
            font_size='14sp'
        )
        self.update_btn = Button(
            text="Check for OTA Updates", 
            size_hint=(1, 0.25),
            background_color=(0, 0.6, 0.8, 1)
        )
        self.update_btn.bind(on_press=self.trigger_ota_check)
        
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.update_btn)
        
        # 2. Check and request Android system hardware permissions at boot
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.INTERNET])
            
        # 3. Spin up the background frame server processing thread
        threading.Thread(target=self.start_camera_server, daemon=True).start()
        
        return self.layout

    def safe_ui_update(self, text_string):
        """Schedules UI text changes safely onto Kivy's main thread loop."""
        self.info_label.text = text_string

    def trigger_ota_check(self, instance):
        self.safe_ui_update("Querying remote cloud server for updates...")
        threading.Thread(target=self.query_github_for_updates, daemon=True).start()

    def query_github_for_updates(self):
        """Queries GitHub API to match local version tags against the latest release."""
        try:
            req = urllib.request.Request(
                GITHUB_API_URL, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get("tag_name", "1.0.0")
                
                # Check for release assets or default to the release webpage
                if data.get("assets"):
                    download_url = data["assets"][0]["browser_download_url"]
                else:
                    download_url = data.get("html_url", "https://github.com")
                
                if latest_version != CURRENT_VERSION:
                    Clock.schedule_once(lambda dt: self.safe_ui_update(f"Update Found ({latest_version})! Redirecting..."), 0)
                    webbrowser.open(download_url)
                else:
                    Clock.schedule_once(lambda dt: self.safe_ui_update("System up to date. Running latest release."), 0)
        except Exception:
            Clock.schedule_once(lambda dt: self.safe_ui_update("OTA Check Failed: Network error or bad API path."), 0)

    def start_camera_server(self):
        """Main camera acquisition loop. Shakes hands over TCP and streams downscaled frames."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind to port 8089 on all available network interfaces
        try:
            server_socket.bind(('0.0.0.0', 8089))
            server_socket.listen(1)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.safe_ui_update(f"Socket Bind Failed: {str(e)}"), 0)
            return

        # Attempt to access mobile device camera back lens
        cap = cv2.VideoCapture(0)
        
        while True:
            Clock.schedule_once(lambda dt: self.safe_ui_update("Waiting for Command Center Handshake..."), 0)
            conn, addr = server_socket.accept()
            Clock.schedule_once(lambda dt: self.safe_ui_update(f"Connected to Center Host: {addr[0]}"), 0)
            
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: 
                        break
                    
                    # --- MOBILE EDGE PROCESSING LEVEL ---
                    # Downscale resolution to 320x240 to keep network throughput ultra-fast
                    frame = cv2.resize(frame, (320, 240)) 
                    
                    # Compress raw arrays into lightweight JPEG format
                    _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
                    
                    # Package frame payload structure
                    data = pickle.dumps(encoded_frame)
                    payload_size = struct.pack("Q", len(data))
                    
                    # Push bytes out to local network
                    conn.sendall(payload_size + data)
            except Exception:
                pass
            finally:
                conn.close()

if __name__ == '__main__':
    SentinelMobileApp().run()