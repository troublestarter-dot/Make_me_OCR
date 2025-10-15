"""Duplicate detection module for OCR Factory."""
import json
from pathlib import Path
from typing import Optional, List, Dict
import imagehash
from PIL import Image
from pdf2image import convert_from_path


class DuplicateChecker:
    """Check for duplicate documents."""
    
    def __init__(self, logger, index_folder: Path, similarity_threshold: float = 0.95):
        """
        Initialize duplicate checker.
        
        Args:
            logger: Logger instance
            index_folder: Path to index folder
            similarity_threshold: Similarity threshold for duplicates
        """
        self.logger = logger
        self.index_folder = index_folder
        self.similarity_threshold = similarity_threshold
        self.index_file = index_folder / 'document_index.json'
        self._load_index()
    
    def _load_index(self):
        """Load document index from file."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {}
        
        self.logger.debug(f"Loaded index with {len(self.index)} documents")
    
    def _save_index(self):
        """Save document index to file."""
        self.index_folder.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Saved index with {len(self.index)} documents")
    
    def calculate_pdf_hash(self, pdf_path: Path) -> str:
        """
        Calculate perceptual hash of PDF (using first page).
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Perceptual hash string
        """
        # Convert first page to image
        images = convert_from_path(str(pdf_path), first_page=1, last_page=1)
        
        if not images:
            raise ValueError(f"Could not convert PDF to image: {pdf_path}")
        
        # Calculate perceptual hash
        phash = imagehash.phash(images[0])
        
        return str(phash)
    
    def calculate_image_hash(self, image_path: Path) -> str:
        """
        Calculate perceptual hash of image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Perceptual hash string
        """
        image = Image.open(image_path)
        phash = imagehash.phash(image)
        return str(phash)
    
    def calculate_hash(self, file_path: Path) -> str:
        """
        Calculate perceptual hash based on file type.
        
        Args:
            file_path: Path to file
        
        Returns:
            Perceptual hash string
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.calculate_pdf_hash(file_path)
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self.calculate_image_hash(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def hash_similarity(self, hash1: str, hash2: str) -> float:
        """
        Calculate similarity between two hashes.
        
        Args:
            hash1: First hash string
            hash2: Second hash string
        
        Returns:
            Similarity score (0-1)
        """
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        
        # Calculate Hamming distance
        distance = h1 - h2
        
        # Convert to similarity (0-1 scale)
        max_distance = len(hash1) * 4  # Each hex char represents 4 bits
        similarity = 1 - (distance / max_distance)
        
        return similarity
    
    def find_duplicates(self, file_path: Path, document_hash: str) -> List[Dict]:
        """
        Find duplicate documents in the index.
        
        Args:
            file_path: Path to file
            document_hash: Perceptual hash of the document
        
        Returns:
            List of duplicate documents
        """
        duplicates = []
        
        for doc_id, doc_info in self.index.items():
            if 'hash' not in doc_info:
                continue
            
            similarity = self.hash_similarity(document_hash, doc_info['hash'])
            
            if similarity >= self.similarity_threshold:
                duplicates.append({
                    'document_id': doc_id,
                    'similarity': similarity,
                    'file_name': doc_info.get('file_name', 'unknown'),
                    'timestamp': doc_info.get('timestamp', 'unknown')
                })
        
        return duplicates
    
    def add_to_index(self, document_id: str, file_path: Path, 
                     document_hash: str, metadata: dict = None):
        """
        Add document to index.
        
        Args:
            document_id: Unique document ID
            file_path: Path to file
            document_hash: Perceptual hash
            metadata: Additional metadata
        """
        from datetime import datetime
        
        self.index[document_id] = {
            'file_name': file_path.name,
            'hash': document_hash,
            'timestamp': datetime.now().isoformat(),
            'file_size': file_path.stat().st_size,
            'metadata': metadata or {}
        }
        
        self._save_index()
        self.logger.info(f"Added to index: {document_id}")
    
    def check_duplicate(self, file_path: Path) -> Optional[List[Dict]]:
        """
        Check if file is a duplicate.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of duplicates if found, None otherwise
        """
        try:
            document_hash = self.calculate_hash(file_path)
            duplicates = self.find_duplicates(file_path, document_hash)
            
            if duplicates:
                self.logger.warning(f"Found {len(duplicates)} duplicate(s) for: {file_path.name}")
                return duplicates
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error checking duplicates: {e}")
            return None
