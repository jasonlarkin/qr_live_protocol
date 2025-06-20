"""
Command Line Interface for QRLP.

Provides comprehensive CLI for QR Live Protocol operations including
live streaming, verification, and configuration management.
"""

import json
import sys
import time

import click

from .config import QRLPConfig
from .core import QRLiveProtocol
from .web_server import QRLiveWebServer


@click.group()
@click.version_option(version="1.0.0")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Configuration file path (JSON or YAML)",
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, config, debug):
    """
    QR Live Protocol (QRLP) - Generate live, verifiable QR codes for streaming.

    QRLP creates cryptographically verifiable QR codes with timestamps,
    blockchain verification, and identity confirmation for livestreaming
    and official video releases.
    """
    # Initialize context
    ctx.ensure_object(dict)

    # Load configuration
    if config:
        ctx.obj["config"] = QRLPConfig.from_file(config)
    else:
        ctx.obj["config"] = QRLPConfig.from_env()

    # Set debug mode
    if debug:
        ctx.obj["config"].logging_settings.level = "DEBUG"
        ctx.obj["config"].web_settings.debug = True


@cli.command()
@click.option("--port", "-p", type=int, help="Web server port")
@click.option("--host", "-h", default="localhost", help="Web server host")
@click.option("--interval", "-i", type=float, help="Update interval in seconds")
@click.option("--no-browser", is_flag=True, help="Do not auto-open browser")
@click.option("--identity-file", type=click.Path(), help="Identity file path")
@click.pass_context
def live(ctx, port, host, interval, no_browser, identity_file):
    """Start live QR code generation and web display."""
    config = ctx.obj["config"]

    # Override settings from command line
    if port:
        config.web_settings.port = port
    if host:
        config.web_settings.host = host
    if interval:
        config.update_interval = interval
    if no_browser:
        config.web_settings.auto_open_browser = False
    if identity_file:
        config.identity_settings.identity_file = identity_file

    # Validate configuration
    issues = config.validate()
    if issues:
        click.echo("Configuration issues found:", err=True)
        for issue in issues:
            click.echo(f"  - {issue}", err=True)
        sys.exit(1)

    click.echo(
        f"Starting QRLP live server on {config.web_settings.host}:{config.web_settings.port}"
    )

    try:
        # Initialize QRLP
        qrlp = QRLiveProtocol(config)

        # Initialize web server
        web_server = QRLiveWebServer(config.web_settings)

        # Connect QRLP updates to web server
        qrlp.add_update_callback(web_server.update_qr_display)

        # Start services
        web_server.start_server(threaded=True)
        qrlp.start_live_generation()

        click.echo(f"✓ QRLP server running at: {web_server.get_server_url()}")
        click.echo("Press Ctrl+C to stop...")

        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\nShutting down...")
            qrlp.stop_live_generation()
            web_server.stop_server()
            click.echo("QRLP stopped.")

    except Exception as e:
        click.echo(f"Error starting QRLP: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file for QR image")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "json", "both"]),
    default="png",
    help="Output format",
)
@click.option(
    "--style",
    "-s",
    type=click.Choice(["live", "professional", "minimal"]),
    help="QR code style",
)
@click.option("--include-text", is_flag=True, help="Include text overlay")
@click.pass_context
def generate(ctx, output, format, style, include_text):
    """Generate a single QR code with current verification data."""
    config = ctx.obj["config"]

    try:
        # Initialize QRLP
        qrlp = QRLiveProtocol(config)

        # Generate QR code
        qr_data, qr_image = qrlp.generate_single_qr()

        click.echo(f"Generated QR code with sequence #{qr_data.sequence_number}")
        click.echo(f"Timestamp: {qr_data.timestamp}")
        click.echo(f"Identity: {qr_data.identity_hash[:16]}...")

        if qr_data.blockchain_hashes:
            click.echo(
                f"Blockchain verification: {list(qr_data.blockchain_hashes.keys())}"
            )

        # Handle output
        if output:
            if format in ["png", "both"]:
                png_path = output if output.endswith(".png") else f"{output}.png"
                with open(png_path, "wb") as f:
                    f.write(qr_image)
                click.echo(f"✓ QR image saved to: {png_path}")

            if format in ["json", "both"]:
                json_path = output if output.endswith(".json") else f"{output}.json"
                with open(json_path, "w") as f:
                    json.dump(qr_data.__dict__, f, indent=2, default=str)
                click.echo(f"✓ QR data saved to: {json_path}")
        else:
            # Print QR data to console
            click.echo("\nQR Data:")
            click.echo(json.dumps(qr_data.__dict__, indent=2, default=str))

    except Exception as e:
        click.echo(f"Error generating QR code: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("qr_data", type=str)
@click.option(
    "--tolerance", "-t", type=float, default=30.0, help="Time tolerance in seconds"
)
@click.pass_context
def verify(ctx, qr_data, tolerance):
    """Verify a QR code's data and authenticity."""
    config = ctx.obj["config"]

    try:
        # Initialize QRLP
        qrlp = QRLiveProtocol(config)

        # Verify QR data
        results = qrlp.verify_qr_data(qr_data)

        click.echo("Verification Results:")
        click.echo(f"  Valid JSON: {'✓' if results['valid_json'] else '✗'}")

        if results["valid_json"]:
            click.echo(
                f"  Identity verified: {'✓' if results['identity_verified'] else '✗'}"
            )
            click.echo(f"  Time verified: {'✓' if results['time_verified'] else '✗'}")
            click.echo(
                f"  Blockchain verified: {'✓' if results['blockchain_verified'] else '✗'}"
            )
        else:
            click.echo(f"  Error: {results.get('error', 'Unknown error')}")

        # Overall result
        overall_valid = (
            results["valid_json"]
            and results["identity_verified"]
            and results["time_verified"]
        )

        click.echo(f"\nOverall: {'✓ VALID' if overall_valid else '✗ INVALID'}")

    except Exception as e:
        click.echo(f"Error verifying QR code: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output configuration file path",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml"]),
    default="json",
    help="Configuration format",
)
@click.pass_context
def config_init(ctx, output, format):
    """Initialize a new configuration file with defaults."""
    try:
        config = QRLPConfig()

        if format == "json":
            with open(output, "w") as f:
                json.dump(config.to_dict(), f, indent=2, default=str)
        elif format == "yaml":
            try:
                import yaml

                with open(output, "w") as f:
                    yaml.dump(config.to_dict(), f, default_flow_style=False)
            except ImportError:
                click.echo("PyYAML required for YAML format", err=True)
                sys.exit(1)

        click.echo(f"✓ Configuration file created: {output}")

    except Exception as e:
        click.echo(f"Error creating configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show current QRLP status and statistics."""
    config = ctx.obj["config"]

    try:
        # Initialize QRLP (without starting live generation)
        qrlp = QRLiveProtocol(config)

        # Get statistics
        stats = qrlp.get_statistics()

        click.echo("QRLP Status:")
        click.echo(f"  Running: {'Yes' if stats['running'] else 'No'}")
        click.echo(f"  Total updates: {stats['total_updates']}")
        click.echo(f"  Sequence number: {stats['sequence_number']}")

        if stats["current_qr_data"]:
            qr_data = stats["current_qr_data"]
            click.echo(f"  Current timestamp: {qr_data['timestamp']}")
            click.echo(f"  Identity hash: {qr_data['identity_hash'][:16]}...")

        # Component statistics
        click.echo("\nComponent Statistics:")

        time_stats = stats.get("time_provider_stats", {})
        click.echo("  Time provider:")
        click.echo(f"    Success rate: {time_stats.get('success_rate', 0):.2%}")
        click.echo(f"    Active servers: {time_stats.get('active_servers', 0)}")

        blockchain_stats = stats.get("blockchain_stats", {})
        click.echo("  Blockchain verifier:")
        click.echo(f"    Success rate: {blockchain_stats.get('success_rate', 0):.2%}")
        click.echo(f"    Cached chains: {blockchain_stats.get('cached_chains', [])}")

        identity_stats = stats.get("identity_stats", {})
        click.echo("  Identity manager:")
        click.echo(f"    Hash generations: {identity_stats.get('hash_generations', 0)}")
        click.echo(f"    File count: {identity_stats.get('file_count', 0)}")

    except Exception as e:
        click.echo(f"Error getting status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--alias", "-a", type=str, help="Alias for the file")
@click.pass_context
def add_file(ctx, file_path, alias):
    """Add a file to the identity for verification."""
    config = ctx.obj["config"]

    try:
        qrlp = QRLiveProtocol(config)

        success = qrlp.identity_manager.add_file_to_identity(file_path, alias)

        if success:
            click.echo(f"✓ File added to identity: {file_path}")
            if alias:
                click.echo(f"  Alias: {alias}")
        else:
            click.echo(f"✗ Failed to add file: {file_path}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error adding file: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
