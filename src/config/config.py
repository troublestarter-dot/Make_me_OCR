"""Configuration management for OCR Factory."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Google Service Account
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '')
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    
    # CloudConvert API
    CLOUDCONVERT_API_KEY = os.getenv('CLOUDCONVERT_API_KEY', '')
    
    # OpenAI GPT
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Folder paths
    INPUT_FOLDER = Path(os.getenv('INPUT_FOLDER', BASE_DIR / 'data' / 'input'))
    OUTPUT_FOLDER = Path(os.getenv('OUTPUT_FOLDER', BASE_DIR / 'data' / 'processed'))
    ORIGINALS_FOLDER = Path(os.getenv('ORIGINALS_FOLDER', BASE_DIR / 'data' / 'originals'))
    INDEX_FOLDER = Path(os.getenv('INDEX_FOLDER', BASE_DIR / 'data' / 'index'))
    
    # Processing settings
    MIN_PAGE_CONTENT_THRESHOLD = float(os.getenv('MIN_PAGE_CONTENT_THRESHOLD', '0.05'))
    DUPLICATE_SIMILARITY_THRESHOLD = float(os.getenv('DUPLICATE_SIMILARITY_THRESHOLD', '0.95'))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
    
    # Make.com webhook
    MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL', '')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = Path(os.getenv('LOG_FILE', BASE_DIR / 'logs' / 'ocr_factory.log'))
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        errors = []
        
        if not cls.GOOGLE_SERVICE_ACCOUNT_FILE:
            errors.append("GOOGLE_SERVICE_ACCOUNT_FILE is not set")
        
        if not cls.CLOUDCONVERT_API_KEY:
            errors.append("CLOUDCONVERT_API_KEY is not set")
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        # Create directories if they don't exist
        for folder in [cls.INPUT_FOLDER, cls.OUTPUT_FOLDER, cls.ORIGINALS_FOLDER, cls.INDEX_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
        
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))
        
        return True
