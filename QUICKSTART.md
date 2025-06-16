# QR Live Protocol - Quick Start Guide

## 🚀 One-Command Setup and Launch

To get QRLP running with a live QR code display updating every second:

```bash
python3 main.py
```

This single command will:
1. ✅ Check Python version and system requirements
2. 🏗️  Create virtual environment (if needed for macOS/Linux)
3. 📦 Install all required dependencies (Flask, qrcode, etc.)
4. 🔧 Set up the QRLP package
5. 🌐 Start the web server
6. 📱 Begin live QR generation (updates every 1 second!)
7. 🌍 Automatically open your browser to view the live display

## 🎯 What You'll See

The browser will open to `http://localhost:8080` showing:
- **Live QR Code** updating every second
- **Real-time timestamp** from synchronized time servers
- **Identity hash** from your system fingerprint
- **Blockchain verification** (Bitcoin, Ethereum current block hashes)
- **Verification status** and statistics
- **Raw data display** showing all encoded information

## 🎥 For Livestreaming (OBS Studio)

1. In OBS Studio, add a **Browser Source**
2. Set URL to: `http://localhost:8080/viewer`
3. Set dimensions: Width: 800, Height: 600
4. The QR code will now appear in your stream, updating live!

## ⚙️ Command Options

```bash
# Full setup and demo (default)
python3 main.py

# Quick setup (no package upgrades)
python3 main.py --quick

# Don't auto-open browser
python3 main.py --no-browser

# Use custom port
python3 main.py --port 9000

# Setup only, don't run demo
python3 main.py --setup-only
```

## 🔍 What's in the QR Code

Each QR code contains JSON data with:
```json
{
  "timestamp": "2025-01-11T15:30:45.123Z",
  "sequence_number": 123,
  "identity_hash": "abc123def456...",
  "blockchain_hashes": {
    "bitcoin": "00000000000000000008a...",
    "ethereum": "0x1234567890abcdef..."
  },
  "time_server_verification": [
    {"server": "pool.ntp.org", "offset": 0.002},
    {"server": "time.google.com", "offset": 0.001}
  ],
  "format_version": "1.0.0"
}
```

## 🛑 Stopping the Demo

Press **Ctrl+C** to cleanly stop the demo. This will:
- Stop QR generation
- Shut down the web server
- Display final statistics
- Clean up temporary files

## 🔧 Advanced Usage

### CLI Commands (after setup)
```bash
# Start live QR generation
qrlp live

# Generate single QR code
qrlp generate --output my_qr.png

# Verify QR data
qrlp verify '{"timestamp":"2025-01-11T..."}'

# Check system status
qrlp status

# Initialize config file
qrlp config-init
```

### Direct Python Usage
```python
from src import QRLiveProtocol, QRLPConfig

# Create with custom settings
config = QRLPConfig()
config.update_interval = 0.5  # Update every 0.5 seconds

qrlp = QRLiveProtocol(config)

# Generate single QR
qr_data, qr_image = qrlp.generate_single_qr()

# Start live generation
qrlp.start_live_generation()
```

## 📊 Monitoring

Visit these URLs while the demo is running:
- `http://localhost:8080` - Main interface
- `http://localhost:8080/viewer` - Clean viewer for streaming
- `http://localhost:8080/admin` - Admin panel with statistics
- `http://localhost:8080/api/status` - JSON status endpoint
- `http://localhost:8080/api/verify` - QR verification endpoint

## 🆘 Troubleshooting

### Dependencies Not Installing
```bash
# Update pip first
python3 -m pip install --upgrade pip

# Then run setup
python3 main.py --quick
```

### Port Already in Use
```bash
# Use different port
python3 main.py --port 8081
```

### Browser Doesn't Open
```bash
# Disable auto-open and manually navigate
python3 main.py --no-browser
# Then open: http://localhost:8080
```

### Permission Issues
```bash
# Install for user only
python3 -m pip install --user -r requirements.txt
```

## 🎉 Success Indicators

You'll know everything is working when you see:
1. ✅ Dependency installation messages
2. 🌐 "Web server started on port 8080"
3. 📱 "QR #1 | 2025-01-11T... | Identity: abc123... | Blockchain: 2 chains"
4. 🌍 Browser opens automatically showing live QR codes
5. QR codes visibly changing every second

Enjoy your live, cryptographically verified QR codes! 🔲✨ 