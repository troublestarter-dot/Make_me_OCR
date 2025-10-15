"""Document ID generation for OCR Factory."""
import hashlib
import uuid
from datetime import datetime
from pathlib import Path


class DocumentIDGenerator:
    """Generate unique IDs for documents."""
    
    @staticmethod
    def generate_hash_id(file_path: Path) -> str:
        """
        Generate hash-based ID from file content.
        
        Args:
            file_path: Path to the file
        
        Returns:
            SHA256 hash of the file
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate UUID-based ID.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_timestamp_id() -> str:
        """
        Generate timestamp-based ID.
        
        Returns:
            Timestamp-based ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"DOC_{timestamp}"
    
    @staticmethod
    def generate_composite_id(file_path: Path) -> str:
        """
        Generate composite ID combining timestamp and hash.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Composite ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = DocumentIDGenerator.generate_hash_id(file_path)[:12]
        return f"DOC_{timestamp}_{file_hash}"
