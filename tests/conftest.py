"""Test configuration and fixtures."""

from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
