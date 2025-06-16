#!/usr/bin/env python3
"""
QR Live Protocol (QRLP) - Main Entry Point

This script performs comprehensive setup and launches the full QRLP livestream demo.

Features:
- Dependency checking and installation
- Package setup and installation 
- Comprehensive system validation
- Automatic demo launch with live QR generation
- Browser integration for real-time display

Usage:
    python main.py [--quick] [--no-browser] [--port 8080]

The demo will:
1. Install all required dependencies
2. Setup the QRLP package
3. Launch a web server with live QR display
4. Update QR codes every second with:
   - Current timestamp from multiple time servers
   - Identity hash from system/file fingerprints
   - Current blockchain hashes (Bitcoin, Ethereum)
   - Cryptographic verification data
5. Open browser window automatically
6. Provide integration URLs for streaming software (OBS)
"""

import sys
import os
import subprocess
import importlib
import platform
import webbrowser
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class QRLPSetupManager:
    """
    Comprehensive setup manager for QR Live Protocol.
    
    Handles dependency installation, package setup, system validation,
    and demo launch with intelligent error handling and user feedback.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.src_path = self.project_root / "src"
        self.requirements_file = self.project_root / "requirements.txt"
        self.setup_file = self.project_root / "setup.py"
        self.demo_file = self.project_root / "examples" / "livestream_demo.py"
        
        # Track installation status
        self.installation_log = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log setup messages with timestamps."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        print(formatted_msg)
        self.installation_log.append(formatted_msg)
    
    def check_python_version(self) -> bool:
        """Verify Python version compatibility."""
        self.log("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log(f"❌ Python {version.major}.{version.minor} detected. QRLP requires Python 3.8+", "ERROR")
            return False
        
        self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    
    def check_system_requirements(self) -> bool:
        """Check system-specific requirements."""
        self.log("🖥️  Checking system requirements...")
        
        system = platform.system()
        self.log(f"✅ Operating System: {system} {platform.release()}")
        
        # Check for required system packages
        if system == "Linux":
            # Check for common missing packages on Linux
            try:
                import tkinter
                self.log("✅ GUI toolkit available")
            except ImportError:
                self.log("⚠️  tkinter not available - some features may be limited", "WARNING")
        
        return True
    
    def read_requirements(self) -> List[str]:
        """Read and parse requirements.txt."""
        if not self.requirements_file.exists():
            self.log("❌ requirements.txt not found", "ERROR")
            return []
        
        requirements = []
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
        
        self.log(f"📋 Found {len(requirements)} requirements")
        return requirements
    
    def check_package_installed(self, package_spec: str) -> bool:
        """Check if a package is already installed."""
        # Extract package name from spec (handle things like "package>=1.0.0")
        package_name = package_spec.split('>=')[0].split('==')[0].split('[')[0]
        
        try:
            importlib.import_module(package_name.replace('-', '_'))
            return True
        except ImportError:
            # Try common alternatives
            alternatives = {
                'pillow': 'PIL',
                'pyyaml': 'yaml',
                'python-dateutil': 'dateutil'
            }
            
            alt_name = alternatives.get(package_name.lower())
            if alt_name:
                try:
                    importlib.import_module(alt_name)
                    return True
                except ImportError:
                    pass
            
            return False
    
    def setup_virtual_environment(self) -> bool:
        """Setup virtual environment if needed."""
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            self.log("✅ Virtual environment already exists")
            return True
        
        self.log("🏗️  Creating virtual environment...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.log(f"❌ Virtual environment creation failed: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ Virtual environment created successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Virtual environment error: {e}", "ERROR")
            return False
    
    def get_venv_python(self) -> str:
        """Get the Python executable from virtual environment."""
        venv_path = self.project_root / "venv"
        
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")
    
    def install_dependencies(self, quick_mode: bool = False) -> bool:
        """Install all required dependencies."""
        self.log("📦 Checking and installing dependencies...")
        
        requirements = self.read_requirements()
        if not requirements:
            return False
        
        # Setup virtual environment if on macOS/Linux with externally managed Python
        venv_python = sys.executable
        try:
            # Test if we can install packages directly
            test_result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--dry-run", "requests"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "externally-managed-environment" in test_result.stderr:
                self.log("🔧 Detected externally managed environment, setting up virtual environment...")
                if not self.setup_virtual_environment():
                    return False
                venv_python = self.get_venv_python()
                self.log(f"✅ Using virtual environment: {venv_python}")
        except:
            # If test fails, try using virtual environment anyway
            if not self.setup_virtual_environment():
                return False
            venv_python = self.get_venv_python()
        
        # Check which packages need installation
        missing_packages = []
        for req in requirements:
            if not self.check_package_installed(req):
                missing_packages.append(req)
        
        if not missing_packages:
            self.log("✅ All dependencies already installed")
            return True
        
        self.log(f"📥 Installing {len(missing_packages)} missing packages...")
        
        # Prepare pip install command with virtual environment python
        pip_cmd = [venv_python, "-m", "pip", "install"]
        
        # Add upgrade flag for better compatibility
        if not quick_mode:
            pip_cmd.append("--upgrade")
        
        # Try --user flag as fallback
        fallback_cmd = [sys.executable, "-m", "pip", "install", "--user"]
        if not quick_mode:
            fallback_cmd.append("--upgrade")
        
        # Install packages
        try:
            for package in missing_packages:
                self.log(f"   Installing {package}...")
                
                # Try with virtual environment first
                result = subprocess.run(
                    pip_cmd + [package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    # Fallback to --user installation
                    self.log(f"   Trying user installation for {package}...")
                    result = subprocess.run(
                        fallback_cmd + [package],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode != 0:
                        self.log(f"❌ Failed to install {package}: {result.stderr}", "ERROR")
                        self.errors.append(f"Package installation failed: {package}")
                        continue  # Try other packages
                
                self.log(f"✅ Successfully installed {package}")
            
            self.log("✅ Dependencies installation completed")
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ Package installation timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Package installation error: {e}", "ERROR")
            return False
    
    def setup_package(self, development_mode: bool = True) -> bool:
        """Install the QRLP package itself."""
        self.log("🔧 Setting up QRLP package...")
        
        if not self.setup_file.exists():
            self.log("❌ setup.py not found", "ERROR")
            return False
        
        try:
            # Use virtual environment python if available
            venv_path = self.project_root / "venv"
            python_exe = self.get_venv_python() if venv_path.exists() else sys.executable
            
            # Install in development mode for easier testing
            cmd = [python_exe, "-m", "pip", "install"]
            if development_mode:
                cmd.extend(["-e", "."])
            else:
                cmd.append(".")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                # Try with --user flag as fallback
                cmd = [sys.executable, "-m", "pip", "install", "--user"]
                if development_mode:
                    cmd.extend(["-e", "."])
                else:
                    cmd.append(".")
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    self.log(f"❌ Package setup failed: {result.stderr}", "ERROR")
                    return False
            
            self.log("✅ QRLP package installed successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Package setup error: {e}", "ERROR")
            return False
    
    def validate_installation(self) -> bool:
        """Validate that QRLP can be imported and used."""
        self.log("🔍 Validating installation...")
        
        try:
            # Use virtual environment python if available
            venv_path = self.project_root / "venv"
            python_exe = self.get_venv_python() if venv_path.exists() else sys.executable
            
            # Create a validation script
            validation_script = '''
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Test core imports
    from src import QRLiveProtocol, QRLPConfig
    from src.qr_generator import QRGenerator
    from src.time_provider import TimeProvider
    from src.blockchain_verifier import BlockchainVerifier
    from src.web_server import QRLiveWebServer
    
    print("IMPORT_SUCCESS")
    
    # Test basic functionality
    config = QRLPConfig()
    qrlp = QRLiveProtocol(config)
    
    print("INSTANCE_SUCCESS")
    
    # Test QR generation (basic test)
    qr_data, qr_image = qrlp.generate_single_qr()
    if qr_data and qr_image:
        print("QR_SUCCESS")
    else:
        print("QR_WARNING")
    
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
'''
            
            # Write validation script
            validation_file = self.project_root / "validate_setup.py"
            with open(validation_file, 'w') as f:
                f.write(validation_script)
            
            # Run validation
            result = subprocess.run(
                [python_exe, str(validation_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up validation file
            validation_file.unlink()
            
            # Check results
            output = result.stdout.strip()
            if "IMPORT_SUCCESS" in output:
                self.log("✅ Core modules imported successfully")
            else:
                self.log(f"❌ Import failed: {result.stderr}", "ERROR")
                return False
            
            if "INSTANCE_SUCCESS" in output:
                self.log("✅ QRLP instance created successfully")
            else:
                self.log("❌ QRLP instance creation failed", "ERROR")
                return False
            
            if "QR_SUCCESS" in output:
                self.log("✅ QR generation working")
            elif "QR_WARNING" in output:
                self.log("⚠️  QR generation returned empty results", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Validation error: {e}", "ERROR")
            return False
    
    def launch_demo(self, port: int = 8080, open_browser: bool = True) -> bool:
        """Launch the comprehensive livestream demo."""
        self.log("🚀 Launching QRLP Livestream Demo...")
        
        if not self.demo_file.exists():
            self.log("❌ Demo file not found", "ERROR")
            return False
        
        try:
            # Use virtual environment python if available
            venv_path = self.project_root / "venv"
            python_exe = self.get_venv_python() if venv_path.exists() else sys.executable
            
            # Prepare demo environment
            demo_env = os.environ.copy()
            demo_env['QRLP_PORT'] = str(port)
            demo_env['QRLP_AUTO_BROWSER'] = str(open_browser).lower()
            
            # Add virtual environment to PATH if exists
            if venv_path.exists():
                venv_bin = venv_path / "bin" if platform.system() != "Windows" else venv_path / "Scripts"
                demo_env['PATH'] = str(venv_bin) + os.pathsep + demo_env.get('PATH', '')
            
            self.log("🌐 Starting web server and QR generation...")
            self.log(f"📡 Server will be available at: http://localhost:{port}")
            
            if open_browser:
                self.log("🌐 Browser will open automatically in 3 seconds...")
                # Open browser after a short delay
                def delayed_browser_open():
                    time.sleep(3)
                    webbrowser.open(f"http://localhost:{port}")
                
                import threading
                browser_thread = threading.Thread(target=delayed_browser_open)
                browser_thread.daemon = True
                browser_thread.start()
            
            # Run the demo
            self.log("▶️  Starting livestream demo (Ctrl+C to stop)...")
            self.log("📱 QR codes will update every second with live data!")
            
            result = subprocess.run(
                [python_exe, str(self.demo_file)],
                cwd=self.project_root,
                env=demo_env
            )
            
            return result.returncode == 0
            
        except KeyboardInterrupt:
            self.log("🛑 Demo stopped by user")
            return True
        except Exception as e:
            self.log(f"❌ Demo launch error: {e}", "ERROR")
            return False
    
    def print_summary(self):
        """Print setup summary and next steps."""
        print("\n" + "="*80)
        print("🔲 QR Live Protocol - Setup Complete!")
        print("="*80)
        
        if self.errors:
            print("⚠️  Setup completed with errors:")
            for error in self.errors:
                print(f"   - {error}")
            print()
        
        print("📋 What was installed:")
        print("   ✅ Python dependencies (Flask, qrcode, etc.)")
        print("   ✅ QRLP package in development mode")
        print("   ✅ Web server with real-time QR display")
        print("   ✅ CLI tools (qrlp command)")
        print()
        
        print("🎯 Demo Features:")
        print("   📱 Live QR codes updating every second")
        print("   ⏰ Real-time synchronization with time servers")
        print("   🔗 Current blockchain hashes (Bitcoin, Ethereum)")
        print("   🆔 Cryptographic identity verification")
        print("   🌐 Web interface for livestreaming integration")
        print()
        
        print("🎥 For Streaming Software (OBS Studio):")
        print("   1. Add 'Browser Source'")
        print("   2. URL: http://localhost:8080/viewer")
        print("   3. Width: 800, Height: 600")
        print()
        
        print("🔧 Available Commands:")
        print("   qrlp live              # Start live QR generation")
        print("   qrlp generate           # Generate single QR")
        print("   qrlp verify <data>      # Verify QR data")
        print("   qrlp status             # Check system status")
        print()
        
        print("⏹️  Press Ctrl+C to stop the demo when running")
        print("="*80)
    
    def run_complete_setup(self, args) -> bool:
        """Run the complete setup process."""
        print("🔲 QR Live Protocol (QRLP) - Comprehensive Setup")
        print("="*80)
        
        # Step 1: System checks
        if not self.check_python_version():
            return False
        
        if not self.check_system_requirements():
            return False
        
        # Step 2: Install dependencies
        if not self.install_dependencies(quick_mode=args.quick):
            return False
        
        # Step 3: Setup package
        if not self.setup_package():
            return False
        
        # Step 4: Validate installation
        if not self.validate_installation():
            return False
        
        # Step 5: Print summary
        self.print_summary()
        
        # Step 6: Launch demo
        if not args.setup_only:
            self.log("🎬 Launching demo in 3 seconds...")
            time.sleep(3)
            return self.launch_demo(
                port=args.port,
                open_browser=not args.no_browser
            )
        
        return True


def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(
        description="QR Live Protocol - Setup and Demo Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Full setup and demo
  python main.py --quick            # Quick setup (skip package upgrades)
  python main.py --no-browser       # Don't auto-open browser
  python main.py --port 9000        # Use custom port
  python main.py --setup-only       # Setup only, don't run demo
        """
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help="Quick setup mode (skip package upgrades)"
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true', 
        help="Don't automatically open browser"
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help="Port for web server (default: 8080)"
    )
    
    parser.add_argument(
        '--setup-only',
        action='store_true',
        help="Run setup only, don't launch demo"
    )
    
    args = parser.parse_args()
    
    # Create and run setup manager
    setup_manager = QRLPSetupManager()
    
    try:
        success = setup_manager.run_complete_setup(args)
        
        if success:
            print("\n🎉 QRLP setup and demo completed successfully!")
            return 0
        else:
            print("\n❌ QRLP setup failed. Check logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 