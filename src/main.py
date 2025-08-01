"""Main entry point for Agentical application."""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from utils.config import ConfigManager
from utils.logger import logger
from ui.main_window import MainWindow


def setup_directories():
    """Create necessary directories."""
    directories = ['logs', 'screenshots', 'recordings', 'config']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Agentical - AI Desktop Automation")
    parser.add_argument('--config', type=str, default='config',
                       help='Configuration directory path')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--version', action='version', version='Agentical 1.0.0')
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Set up directories
        setup_directories()
        
        # Initialize configuration
        config = ConfigManager(args.config)
        
        # Override debug mode if specified
        if args.debug:
            config.set('app.debug', True)
        
        logger.info("=" * 50)
        logger.info("Starting Agentical - AI Desktop Automation")
        logger.info("=" * 50)
        
        # Validate configuration
        if not config.api_key:
            logger.warning("Gemini API key not configured. Please set it in the configuration dialog.")
        
        # Create and run main window
        app = MainWindow(config)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error_with_context(e, "main application")
        sys.exit(1)


if __name__ == "__main__":
    main()