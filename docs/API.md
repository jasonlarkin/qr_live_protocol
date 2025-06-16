# QRLP API Reference

## Python API

### QRLiveProtocol Class

The main coordinator class that manages all QRLP components.

#### Constructor

```python
from src import QRLiveProtocol, QRLPConfig

# Initialize with default configuration
qrlp = QRLiveProtocol()

# Initialize with custom configuration
config = QRLPConfig()
config.update_interval = 2.0
qrlp = QRLiveProtocol(config)
```

#### Methods

##### `start_live_generation()`
Start continuous QR code generation in a background thread.

```python
qrlp.start_live_generation()
```

##### `stop_live_generation()`
Stop continuous QR code generation.

```python
qrlp.stop_live_generation()
```

##### `generate_single_qr(user_data=None)`
Generate a single QR code with current verification data.

**Parameters:**
- `user_data` (dict, optional): Additional data to include in QR code

**Returns:**
- `tuple`: (QRData object, QR image as bytes)

```python
qr_data, qr_image = qrlp.generate_single_qr()

# With custom data
custom_data = {"event": "livestream", "video_id": "abc123"}
qr_data, qr_image = qrlp.generate_single_qr(custom_data)
```

##### `verify_qr_data(qr_json)`
Verify QR code data integrity and authenticity.

**Parameters:**
- `qr_json` (str): JSON string from QR code

**Returns:**
- `dict`: Verification results

```python
qr_json = '{"timestamp":"2025-01-16T...","identity_hash":"abc123..."}'
results = qrlp.verify_qr_data(qr_json)

print(results['valid_json'])        # True if JSON is valid
print(results['identity_verified']) # True if identity matches
print(results['time_verified'])     # True if timestamp is recent
print(results['blockchain_verified']) # True if blockchain data is current
```

##### `add_update_callback(callback)`
Add callback function for QR update events.

**Parameters:**
- `callback` (function): Function with signature `(qr_data, qr_image)`

```python
def handle_qr_update(qr_data, qr_image):
    print(f"New QR: #{qr_data.sequence_number}")
    # Save image to file
    with open(f"qr_{qr_data.sequence_number}.png", "wb") as f:
        f.write(qr_image)

qrlp.add_update_callback(handle_qr_update)
```

##### `get_statistics()`
Get performance and usage statistics.

**Returns:**
- `dict`: Statistics dictionary

```python
stats = qrlp.get_statistics()
print(f"Total updates: {stats['total_updates']}")
print(f"Running: {stats['running']}")
print(f"Sequence number: {stats['sequence_number']}")
```

### QRData Class

Data structure representing QR code payload.

#### Attributes

```python
@dataclass
class QRData:
    timestamp: str                    # ISO format timestamp
    identity_hash: str               # SHA-256 identity hash
    blockchain_hashes: Dict[str, str] # Chain -> block hash mapping
    time_server_verification: Dict    # Time server verification data
    user_data: Optional[Dict] = None  # Optional user data
    sequence_number: int = 0         # Sequential number
```

#### Methods

##### `to_json()`
Convert QRData to JSON string for QR encoding.

```python
qr_data = QRData(...)
json_str = qr_data.to_json()
```

##### `from_json(json_str)`
Create QRData from JSON string (class method).

```python
qr_data = QRData.from_json(json_str)
```

### Configuration Classes

#### QRLPConfig

Main configuration container.

```python
from src.config import QRLPConfig

config = QRLPConfig()
config.update_interval = 5.0        # Seconds between QR updates
config.qr_settings.box_size = 12    # QR code box size
config.web_settings.port = 8080     # Web server port
```

#### QRSettings

QR code generation settings.

```python
config.qr_settings.error_correction_level = "M"  # L, M, Q, H
config.qr_settings.box_size = 10
config.qr_settings.border_size = 4
config.qr_settings.fill_color = "black"
config.qr_settings.back_color = "white"
```

#### BlockchainSettings

Blockchain verification settings.

```python
config.blockchain_settings.enabled_chains = {"bitcoin", "ethereum"}
config.blockchain_settings.cache_duration = 300  # seconds
config.blockchain_settings.timeout = 10.0
```

## REST API

When running the web server, QRLP provides REST endpoints.

### Base URL
`http://localhost:8080` (default)

### Endpoints

#### `GET /api/status`
Get system status and statistics.

**Response:**
```json
{
  "is_running": true,
  "page_views": 42,
  "websocket_connections": 2,
  "qr_updates_sent": 156,
  "server_url": "http://localhost:8080",
  "current_qr_available": true
}
```

#### `GET /api/qr/current`
Get current QR code data and image.

**Response:**
```json
{
  "qr_data": {
    "timestamp": "2025-01-16T19:30:45.123Z",
    "identity_hash": "abc123def456...",
    "blockchain_hashes": {
      "bitcoin": "00000000000000000008a...",
      "ethereum": "0x1234567890abcdef..."
    },
    "time_server_verification": {...},
    "sequence_number": 123,
    "user_data": null
  },
  "qr_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "timestamp": "2025-01-16T19:30:45.456Z"
}
```

#### `POST /api/verify`
Verify QR code data.

**Request:**
```json
{
  "qr_data": "{\"timestamp\":\"2025-01-16T...\",\"identity_hash\":\"abc123...\"}"
}
```

**Response:**
```json
{
  "valid": true,
  "timestamp": "2025-01-16T19:30:45.789Z",
  "message": "QR data verification successful",
  "details": {
    "valid_json": true,
    "identity_verified": true,
    "time_verified": true,
    "blockchain_verified": true
  }
}
```

## WebSocket API

Real-time updates via Socket.IO.

### Connection
```javascript
const socket = io('http://localhost:8080');
```

### Events

#### `connect`
Triggered when client connects to server.

```javascript
socket.on('connect', function() {
    console.log('Connected to QRLP server');
});
```

#### `qr_update`
Triggered when new QR code is generated.

```javascript
socket.on('qr_update', function(data) {
    console.log('New QR data:', data.qr_data);
    console.log('QR image:', data.qr_image);
});
```

#### `request_qr_update`
Request current QR code data.

```javascript
socket.emit('request_qr_update');
```

## Command Line Interface

### Global Options

- `--config, -c`: Configuration file path
- `--debug, -d`: Enable debug mode
- `--help, -h`: Show help message

### Commands

#### `qrlp live`
Start live QR generation with web interface.

```bash
# Basic usage
qrlp live

# Custom port and host
qrlp live --port 8081 --host 0.0.0.0

# No auto-browser
qrlp live --no-browser

# Custom update interval
qrlp live --interval 2.0

# With identity file
qrlp live --identity-file ./my-key.pem
```

**Options:**
- `--port`: Web server port (default: 8080)
- `--host`: Web server host (default: localhost)
- `--no-browser`: Don't auto-open browser
- `--interval`: Update interval in seconds
- `--identity-file`: Path to identity file

#### `qrlp generate`
Generate single QR code.

```bash
# Basic generation
qrlp generate

# Save to file
qrlp generate --output qr_code.png

# With custom style
qrlp generate --style professional --include-text

# JSON data only
qrlp generate --format json --output data.json

# Both image and JSON
qrlp generate --format both --output qr_code
```

**Options:**
- `--output, -o`: Output file path
- `--style`: QR style (live, professional, minimal)
- `--include-text`: Add text overlay
- `--format`: Output format (image, json, both)

#### `qrlp verify`
Verify QR code data.

```bash
# Verify JSON string
qrlp verify '{"timestamp":"2025-01-16T...","identity_hash":"abc123..."}'

# Verify from file
qrlp verify --file qr_data.json

# Detailed output
qrlp verify --verbose '{"timestamp":"..."}'
```

**Options:**
- `--file, -f`: Read data from file
- `--verbose, -v`: Show detailed verification results

#### `qrlp status`
Show current system status.

```bash
qrlp status
```

#### `qrlp config-init`
Create configuration file.

```bash
# Default location
qrlp config-init

# Custom location
qrlp config-init --output ./config.json

# With comments
qrlp config-init --with-comments
```

## Integration Examples

### Flask Integration

```python
from flask import Flask, jsonify
from src import QRLiveProtocol

app = Flask(__name__)
qrlp = QRLiveProtocol()

@app.route('/qr/generate')
def generate_qr():
    qr_data, qr_image = qrlp.generate_single_qr()
    return jsonify({
        'data': qr_data.__dict__,
        'image_base64': base64.b64encode(qr_image).decode()
    })

if __name__ == '__main__':
    qrlp.start_live_generation()
    app.run()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from src import QRLiveProtocol
import base64

app = FastAPI()
qrlp = QRLiveProtocol()

@app.get("/qr/current")
async def get_current_qr():
    qr_data, qr_image = qrlp.generate_single_qr()
    return {
        "data": qr_data.__dict__,
        "image": base64.b64encode(qr_image).decode()
    }

@app.on_event("startup")
async def startup_event():
    qrlp.start_live_generation()
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from src import QRLiveProtocol
import base64

qrlp = QRLiveProtocol()
qrlp.start_live_generation()

def get_qr_code(request):
    qr_data, qr_image = qrlp.generate_single_qr()
    return JsonResponse({
        'data': qr_data.__dict__,
        'image': base64.b64encode(qr_image).decode()
    })
```

## Error Handling

### Common Exceptions

```python
from src.exceptions import QRLPError, ConfigurationError, BlockchainError

try:
    qrlp = QRLiveProtocol(config)
    qr_data, qr_image = qrlp.generate_single_qr()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except BlockchainError as e:
    print(f"Blockchain verification failed: {e}")
except QRLPError as e:
    print(f"QRLP error: {e}")
```

### HTTP Error Responses

#### 400 Bad Request
```json
{
  "error": "Invalid QR data format",
  "details": "JSON parsing failed"
}
```

#### 404 Not Found
```json
{
  "error": "No QR data available",
  "message": "QR generation not started"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Blockchain API temporarily unavailable"
}
```

## Performance Considerations

### Memory Usage
- Base memory usage: ~50MB
- Additional ~10MB per 1000 cached QR codes
- Blockchain cache: ~5MB per chain

### CPU Usage
- QR generation: ~1-5ms per QR code
- Blockchain verification: ~100-500ms (cached: ~1ms)
- Time synchronization: ~50-200ms (cached: ~1ms)

### Network Usage
- Blockchain API calls: ~1KB per request
- Time server queries: ~100 bytes per request
- Web interface: ~50KB initial load, ~5KB per QR update

### Optimization Tips

1. **Increase cache duration** for blockchain data
2. **Reduce update interval** for better performance
3. **Disable unused blockchain chains**
4. **Use local time servers** when possible
5. **Configure appropriate error correction level**

---

For more examples and advanced usage, see the [examples/](../examples/) directory. 