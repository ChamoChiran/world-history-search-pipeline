from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
RAW_DATA_DIR = PROJECT_ROOT / "data/raw"
EXTRACTED_DATA_DIR = PROJECT_ROOT / "data/extracted"
CLEAN_DATA_DIR = PROJECT_ROOT / "data/clean"