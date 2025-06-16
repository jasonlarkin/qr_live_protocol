# QRLP Configuration Guide

## Configuration Methods

QRLP can be configured through multiple methods, listed in order of precedence:

1. **Command line arguments** (highest priority)
2. **Environment variables**
3. **Configuration file**
4. **Default values** (lowest priority)

## Configuration File

### Creating a Configuration File

```bash
# Generate default configuration file
qrlp config-init --output ~/.qrlp/config.json

# Generate with comments and examples
qrlp config-init --with-comments --output config.json
```

### Configuration File Format

```json
{
  "update_interval": 5.0,
  "qr_settings": {
    "error_correction_level": "M",
    "box_size": 10,
    "border_size": 4,
    "fill_color": "black",
    "back_color": "white"
  },
  "web_settings": {
    "host": "localhost",
    "port": 8080,
    "auto_open_browser": true,
    "cors_enabled": false
  },
  "blockchain_settings": {
    "enabled_chains": ["bitcoin", "ethereum"],
    "cache_duration": 300,
    "timeout": 10.0,
    "retry_attempts": 3
  },
  "time_settings": {
    "time_servers": [
      "time.nist.gov",
      "pool.ntp.org",
      "time.google.com",
      "time.cloudflare.com"
    ],
    "update_interval": 60.0,
    "timeout": 5.0
  },
  "identity_settings": {
    "identity_file": null,
    "auto_generate": true,
    "include_system_info": true,
    "hash_algorithm": "sha256"
  },
  "verification_settings": {
    "max_time_drift": 300.0,
    "require_blockchain": false,
    "require_time_server": false
  }
}
```

## Configuration Options

### Core Settings

#### `update_interval`
**Type:** `float`  
**Default:** `5.0`  
**Description:** Interval in seconds between QR code updates.

```json
"update_interval": 2.0  // Update every 2 seconds
```

### QR Code Settings (`qr_settings`)

#### `error_correction_level`
**Type:** `string`  
**Default:** `"M"`  
**Options:** `"L"`, `"M"`, `"Q"`, `"H"`  
**Description:** QR code error correction level.

- `L`: ~7% correction
- `M`: ~15% correction (recommended for most uses)
- `Q`: ~25% correction
- `H`: ~30% correction (best for damaged codes)

#### `box_size`
**Type:** `integer`  
**Default:** `10`  
**Description:** Size of each QR code box in pixels.

```json
"box_size": 12  // Larger QR codes for better visibility
```

#### `border_size`
**Type:** `integer`  
**Default:** `4`  
**Description:** Border size around QR code in boxes.

#### `fill_color` / `back_color`
**Type:** `string`  
**Default:** `"black"` / `"white"`  
**Description:** QR code colors (any valid color name or hex).

```json
"fill_color": "#000000",
"back_color": "#ffffff"
```

### Web Server Settings (`web_settings`)

#### `host`
**Type:** `string`  
**Default:** `"localhost"`  
**Description:** Web server bind address.

```json
"host": "0.0.0.0"  // Allow external connections
```

#### `port`
**Type:** `integer`  
**Default:** `8080`  
**Description:** Web server port.

#### `auto_open_browser`
**Type:** `boolean`  
**Default:** `true`  
**Description:** Automatically open browser when starting web server.

#### `cors_enabled`
**Type:** `boolean`  
**Default:** `false`  
**Description:** Enable CORS for API endpoints.

### Blockchain Settings (`blockchain_settings`)

#### `enabled_chains`
**Type:** `array[string]`  
**Default:** `["bitcoin", "ethereum"]`  
**Options:** `"bitcoin"`, `"ethereum"`, `"litecoin"`, `"dogecoin"`  
**Description:** List of blockchain networks to verify against.

```json
"enabled_chains": ["bitcoin"]  // Bitcoin only
```

#### `cache_duration`
**Type:** `float`  
**Default:** `300.0`  
**Description:** How long to cache blockchain data in seconds.

#### `timeout`
**Type:** `float`  
**Default:** `10.0`  
**Description:** Timeout for blockchain API requests.

#### `retry_attempts`
**Type:** `integer`  
**Default:** `3`  
**Description:** Number of retry attempts for failed API requests.

### Time Settings (`time_settings`)

#### `time_servers`
**Type:** `array[string]`  
**Default:** `["time.nist.gov", "pool.ntp.org", "time.google.com", "time.cloudflare.com"]`  
**Description:** List of time servers for synchronization.

```json
"time_servers": [
  "0.pool.ntp.org",
  "1.pool.ntp.org",
  "time.nist.gov"
]
```

#### `update_interval`
**Type:** `float`  
**Default:** `60.0`  
**Description:** How often to update time synchronization.

#### `timeout`
**Type:** `float`  
**Default:** `5.0`  
**Description:** Timeout for time server requests.

### Identity Settings (`identity_settings`)

#### `identity_file`
**Type:** `string` or `null`  
**Default:** `null`  
**Description:** Path to file for identity generation.

```json
"identity_file": "/path/to/key.pem"
```

#### `auto_generate`
**Type:** `boolean`  
**Default:** `true`  
**Description:** Automatically generate identity if no file provided.

#### `include_system_info`
**Type:** `boolean`  
**Default:** `true`  
**Description:** Include system information in identity hash.

#### `hash_algorithm`
**Type:** `string`  
**Default:** `"sha256"`  
**Options:** `"sha256"`, `"sha512"`, `"md5"`  
**Description:** Hash algorithm for identity generation.

### Verification Settings (`verification_settings`)

#### `max_time_drift`
**Type:** `float`  
**Default:** `300.0`  
**Description:** Maximum allowed time drift in seconds for verification.

#### `require_blockchain`
**Type:** `boolean`  
**Default:** `false`  
**Description:** Require blockchain verification for valid QR codes.

#### `require_time_server`
**Type:** `boolean`  
**Default:** `false`  
**Description:** Require time server verification for valid QR codes.

## Environment Variables

All configuration options can be set via environment variables using the prefix `QRLP_` and uppercase names:

```bash
# Core settings
export QRLP_UPDATE_INTERVAL=2.0

# Web settings
export QRLP_WEB_HOST=0.0.0.0
export QRLP_WEB_PORT=8080
export QRLP_WEB_AUTO_OPEN_BROWSER=false

# QR settings
export QRLP_QR_ERROR_CORRECTION_LEVEL=H
export QRLP_QR_BOX_SIZE=12
export QRLP_QR_BORDER_SIZE=6

# Blockchain settings
export QRLP_BLOCKCHAIN_ENABLED_CHAINS=bitcoin,ethereum
export QRLP_BLOCKCHAIN_CACHE_DURATION=600
export QRLP_BLOCKCHAIN_TIMEOUT=15.0

# Time settings
export QRLP_TIME_UPDATE_INTERVAL=30.0
export QRLP_TIME_TIMEOUT=3.0

# Identity settings
export QRLP_IDENTITY_FILE=/path/to/key.pem
export QRLP_IDENTITY_AUTO_GENERATE=true
export QRLP_IDENTITY_INCLUDE_SYSTEM_INFO=false

# Verification settings
export QRLP_VERIFICATION_MAX_TIME_DRIFT=60.0
export QRLP_VERIFICATION_REQUIRE_BLOCKCHAIN=true

# Logging
export QRLP_LOG_LEVEL=DEBUG
```

## Command Line Arguments

Most configuration options can be overridden via command line:

```bash
# Basic options
qrlp live --port 8081 --host 0.0.0.0 --interval 2.0

# No browser auto-open
qrlp live --no-browser

# Custom identity file
qrlp live --identity-file ./my-key.pem

# Debug mode
qrlp live --debug

# Custom configuration file
qrlp live --config ./custom-config.json
```

## Configuration Examples

### Livestreaming Setup

Optimized for streaming with OBS Studio:

```json
{
  "update_interval": 1.0,
  "qr_settings": {
    "error_correction_level": "M",
    "box_size": 12,
    "border_size": 6
  },
  "web_settings": {
    "host": "0.0.0.0",
    "port": 8080,
    "auto_open_browser": true,
    "cors_enabled": true
  },
  "blockchain_settings": {
    "enabled_chains": ["bitcoin", "ethereum"],
    "cache_duration": 180
  }
}
```

### High Security Setup

Maximum verification and security:

```json
{
  "update_interval": 10.0,
  "qr_settings": {
    "error_correction_level": "H"
  },
  "blockchain_settings": {
    "enabled_chains": ["bitcoin", "ethereum", "litecoin"],
    "cache_duration": 60,
    "retry_attempts": 5
  },
  "identity_settings": {
    "identity_file": "/secure/path/identity.key",
    "include_system_info": true,
    "hash_algorithm": "sha512"
  },
  "verification_settings": {
    "max_time_drift": 30.0,
    "require_blockchain": true,
    "require_time_server": true
  }
}
```

### Minimal/Performance Setup

Optimized for speed and minimal resource usage:

```json
{
  "update_interval": 5.0,
  "qr_settings": {
    "error_correction_level": "L",
    "box_size": 8
  },
  "blockchain_settings": {
    "enabled_chains": ["bitcoin"],
    "cache_duration": 900,
    "timeout": 5.0
  },
  "time_settings": {
    "time_servers": ["time.google.com"],
    "update_interval": 300.0
  }
}
```

### Development Setup

Configuration for development and testing:

```json
{
  "update_interval": 2.0,
  "web_settings": {
    "host": "localhost",
    "port": 8080,
    "auto_open_browser": false,
    "cors_enabled": true
  },
  "blockchain_settings": {
    "cache_duration": 30,
    "timeout": 5.0
  },
  "verification_settings": {
    "max_time_drift": 600.0,
    "require_blockchain": false,
    "require_time_server": false
  }
}
```

## Dynamic Configuration

### Runtime Configuration Changes

```python
from src import QRLiveProtocol, QRLPConfig

# Create initial configuration
config = QRLPConfig()
qrlp = QRLiveProtocol(config)

# Update configuration at runtime
qrlp.config.update_interval = 2.0
qrlp.config.blockchain_settings.enabled_chains = {"bitcoin"}

# Restart with new configuration
qrlp.stop_live_generation()
qrlp.start_live_generation()
```

### Configuration Validation

QRLP automatically validates configuration values:

```python
config = QRLPConfig()
config.update_interval = -1.0  # Invalid: raises ConfigurationError
config.qr_settings.error_correction_level = "X"  # Invalid: raises ConfigurationError
```

## Best Practices

### Security
1. **Use strong identity files** for production
2. **Enable blockchain verification** for authenticity
3. **Use HTTPS** in production environments
4. **Restrict network access** with host binding

### Performance
1. **Increase cache duration** for stable environments
2. **Reduce enabled chains** if not all are needed
3. **Use local time servers** when available
4. **Optimize update interval** for your use case

### Reliability
1. **Configure multiple time servers** for redundancy
2. **Set appropriate timeouts** for your network
3. **Enable retry attempts** for API calls
4. **Monitor logs** for configuration issues

### Development
1. **Use short cache durations** for testing
2. **Disable auto-browser** for headless testing
3. **Enable CORS** for web development
4. **Use debug logging** for troubleshooting

---

For more configuration examples, see the [examples/](../examples/) directory. 