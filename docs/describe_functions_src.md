```bash
__init__.py:

__main__.py:

blockchain_verifier.py:
    - __init__(): Initialize blockchain verifier with settings.
    - _initial_update(): Perform initial blockchain data update.
    - get_blockchain_hashes(): Get current blockchain hashes for all enabled chains.
    - get_blockchain_info(): Get detailed blockchain information for a specific chain.
    - get_all_blockchain_info(): Get detailed information for all cached blockchains.
    - verify_blockchain_hash(): Verify if a blockchain hash is recent and valid.
    - force_update(): Force update of blockchain data.
    - get_statistics(): Get blockchain verifier statistics.
    - _update_if_needed(): Update blockchain data if cache is stale.
    - _update_all_chains(): Update all enabled blockchain chains.
    - _update_chain(): Update blockchain data for a specific chain.
    - _make_request_with_fallback(): Make API request with fallback to multiple endpoints.
    - _get_bitcoin_info(): Get Bitcoin blockchain information with improved API handling.
    - _get_ethereum_info(): Get Ethereum blockchain information with simplified API.
    - _get_litecoin_info(): Get Litecoin blockchain information.

cli.py:
    - cli(): QR Live Protocol (QRLP) - Generate live, verifiable QR codes for streaming.
    - live(): Start live QR code generation and web display.
    - generate(): Generate a single QR code with current verification data.
    - verify(): Verify a QR code's data and authenticity.
    - config_init(): Initialize a new configuration file with defaults.
    - status(): Show current QRLP status and statistics.
    - add_file(): Add a file to the identity for verification.

config.py:
    - from_env(): Create configuration from environment variables.
    - from_file(): Load configuration from JSON or YAML file.
    - to_dict(): Convert configuration to dictionary.
    - validate(): Validate configuration and return list of issues.

core.py:
    - to_json(): Convert to JSON string for QR encoding.
    - from_json(): Create QRData from JSON string.
    - __init__(): Initialize QRLP with configuration.
    - add_update_callback(): Add callback function to be called when QR code updates.
    - remove_update_callback(): Remove previously added callback.
    - set_user_data_callback(): Set callback function to get user data for QR generation.
    - start_live_generation(): Start continuous QR code generation in background thread.
    - stop_live_generation(): Stop continuous QR code generation.
    - generate_single_qr(): Generate a single QR code with current time and verification data.
    - get_current_qr_data(): Get the most recently generated QR data.
    - get_statistics(): Get performance and usage statistics.
    - verify_qr_data(): Verify a QR code's data integrity and authenticity.
    - _update_loop(): Main update loop for continuous QR generation.
    - __enter__(): Context manager entry.
    - __exit__(): Context manager exit.

identity_manager.py:
    - __init__(): Initialize identity manager with settings.
    - get_identity_hash(): Get current identity hash.
    - get_identity_info(): Get complete identity information.
    - update_custom_data(): Update custom data in identity.
    - add_file_to_identity(): Add a file hash to the identity.
    - remove_file_from_identity(): Remove a file from identity.
    - export_identity(): Export identity information to file.
    - import_identity(): Import identity information from file.
    - get_statistics(): Get identity manager statistics.
    - _initialize_identity(): Initialize identity information.
    - _create_new_identity(): Create a new identity.
    - _generate_identity_hash(): Generate cryptographic hash of identity.
    - _collect_system_info(): Collect system information for identity.
    - _calculate_file_hash(): Calculate hash of a file.
    - _identity_changed(): Check if identity components have changed.

qr_generator.py:
    - __init__(): Initialize QR generator with settings.
    - generate_qr_image(): Generate QR code image as bytes.
    - generate_chunked_qr_codes(): Generate multiple QR codes for large data by chunking.
    - create_live_display_qr(): Create QR code optimized for live display with text overlay.
    - verify_qr_readability(): Verify QR code readability and quality metrics.
    - get_statistics(): Get generator statistics.
    - _create_qr_instance(): Create QR code instance with current settings.
    - _generate_styled_image(): Generate styled QR code image.
    - _split_data(): Split data into chunks for multiple QR codes.
    - _image_to_bytes(): Convert PIL Image to bytes.
    - _add_text_overlay(): Add text overlay to QR code for live display.

time_provider.py:
    - __init__(): Initialize time provider with settings.
    - get_current_time(): Get current time with best available synchronization.
    - get_time_server_verification(): Get verification data from time servers.
    - verify_timestamp(): Verify if a timestamp is within acceptable range of current time.
    - get_ntp_time(): Get time from specific NTP server.
    - get_http_time(): Get time from HTTP time API.
    - sync_all_servers(): Synchronize with all configured time servers.
    - get_statistics(): Get time provider statistics.
    - _sync_with_servers(): Internal method to synchronize with time servers.
    - force_sync(): Force immediate synchronization with time servers.

web_server.py:
    - __init__(): Initialize web server with settings.
    - start_server(): Start the web server.
    - stop_server(): Stop the web server.
    - update_qr_display(): Update the QR code display with new data.
    - get_server_url(): Get the server URL.
    - get_statistics(): Get web server statistics.
    - get_user_data(): Get current user input data for QR generation.
    - _setup_routes(): Setup Flask routes.
    - _setup_websocket_events(): Setup SocketIO events for real-time updates.
    - _broadcast_qr_update(): Broadcast QR update to all connected clients.
    - _send_qr_update_to_client(): Send QR update to requesting client.
    - _run_server(): Run the Flask server.
    - _open_browser(): Open browser to server URL.
    - _get_template_dir(): Get template directory path.
    - _get_static_dir(): Get static files directory path.
    - index(): Main QR display page.
    - get_current_qr(): API endpoint for current QR data.
    - get_status(): API endpoint for server status.
    - verify_qr(): API endpoint for QR verification.
    - viewer(): QR viewer page for external displays.
    - admin(): Admin interface for monitoring.
    - update_user_data(): API endpoint for updating user data.
    - get_user_data(): API endpoint for getting current user data.
    - handle_connect(): Handle client connection.
    - handle_disconnect(): Handle client disconnection.
    - handle_qr_request(): Handle client request for QR update.
    - handle_user_data_update(): Handle user data update from client.
```
