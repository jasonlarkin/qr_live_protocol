# QRLP Installation Guide

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Memory**: Minimum 512MB RAM
- **Network**: Internet connection for blockchain and time server verification
- **Disk Space**: ~100MB for installation

### Required System Packages

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3 (if not already installed)
brew install python3
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Windows
1. Download Python from [python.org](https://python.org)
2. Ensure "Add Python to PATH" is checked during installation
3. Install Git from [git-scm.com](https://git-scm.com)

## Installation Methods

### Method 1: One-Command Setup (Recommended)

For most users, this is the easiest way to get started:

```bash
# Clone and setup automatically
git clone https://github.com/your-org/qr_live_protocol.git
cd qr_live_protocol
python3 main.py
```

This command will:
- ✅ Check system compatibility
- 🏗️ Create virtual environment (if needed)
- 📦 Install all dependencies automatically
- 🔧 Setup the QRLP package
- 🌐 Start the web server
- 📱 Begin live QR generation
- 🌍 Open browser automatically

### Method 2: Manual Installation

For advanced users who want more control:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/qr_live_protocol.git
cd qr_live_protocol

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install QRLP package
pip install -e .

# 5. Start the demo
python examples/livestream_demo.py
```

### Method 3: Docker Installation

```bash
# Clone repository
git clone https://github.com/your-org/qr_live_protocol.git
cd qr_live_protocol

# Build Docker image
docker build -t qrlp .

# Run QRLP container
docker run -p 8080:8080 qrlp
```

### Method 4: PyPI Installation (Coming Soon)

```bash
# Install from PyPI (when available)
pip install qr-live-protocol

# Start QRLP
qrlp live
```

## Verification

After installation, verify everything is working:

### 1. Check Installation
```bash
python3 -c "from src import QRLiveProtocol; print('✅ QRLP installed successfully')"
```

### 2. Test QR Generation
```bash
qrlp generate --output test_qr.png
```

### 3. Check Web Interface
```bash
qrlp live --no-browser
# Then visit: http://localhost:8080
```

### 4. Verify Blockchain Connection
```bash
qrlp status
```

Expected output should show:
- ✅ System status: Operational
- ✅ Blockchain connections: Active
- ✅ Time servers: Synchronized

## Configuration

### Environment Variables
```bash
export QRLP_UPDATE_INTERVAL=5      # QR update interval in seconds
export QRLP_WEB_PORT=8080          # Web server port
export QRLP_WEB_HOST=localhost     # Web server host
export QRLP_LOG_LEVEL=INFO         # Logging level
```

### Configuration File
```bash
# Generate default configuration
qrlp config-init --output ~/.qrlp/config.json

# Edit configuration
nano ~/.qrlp/config.json
```

## Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Solution 1: Use virtual environment
python3 -m venv venv
source venv/bin/activate
python3 main.py

# Solution 2: User installation
pip install --user -r requirements.txt
```

#### Port Already in Use
```bash
# Use different port
python3 main.py --port 8081
```

#### Dependencies Not Installing
```bash
# Update pip first
python3 -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Try installing manually
pip install Flask qrcode[pil] requests ntplib
```

#### Virtual Environment Issues on macOS
```bash
# If using externally managed Python
python3 -m venv --system-site-packages venv
source venv/bin/activate
python3 main.py
```

#### Network/Firewall Issues
```bash
# Allow connections through firewall
# macOS: System Preferences > Security & Privacy > Firewall
# Linux: sudo ufw allow 8080
# Windows: Windows Defender Firewall settings
```

### Getting Help

1. **Check Logs**: Enable debug mode with `--debug` flag
2. **GitHub Issues**: Report bugs at [github.com/your-org/qr_live_protocol/issues](https://github.com/your-org/qr_live_protocol/issues)
3. **Documentation**: Full docs at [docs/README.md](README.md)
4. **Community**: Join discussions in GitHub Discussions

## Uninstallation

### Remove QRLP
```bash
# If installed via pip
pip uninstall qr-live-protocol

# If installed from source
cd qr_live_protocol
pip uninstall -e .

# Remove configuration
rm -rf ~/.qrlp/
```

### Clean Virtual Environment
```bash
# Remove virtual environment
rm -rf venv/
```

## Security Considerations

### Network Security
- QRLP runs a web server on localhost by default
- For production use, consider HTTPS and firewall rules
- Blockchain API calls are read-only and safe

### Data Privacy
- Identity hashes are cryptographic and don't expose personal data
- No personal information is transmitted to external services
- All blockchain queries are anonymous

### Production Deployment
For production use:
1. Use a WSGI server (gunicorn, uwsgi)
2. Configure HTTPS with SSL certificates
3. Set up proper firewall rules
4. Monitor logs and performance
5. Consider using environment variables for sensitive configuration

## Next Steps

After successful installation:
1. Read the [Quick Start Guide](../QUICKSTART.md)
2. Explore [Configuration Options](CONFIGURATION.md)
3. Try [Examples](../examples/)
4. Set up [OBS Integration](STREAMING.md)
5. Check out the [API Reference](API.md)

---

**Need help?** Open an issue on [GitHub](https://github.com/your-org/qr_live_protocol/issues) or check our [FAQ](FAQ.md). 