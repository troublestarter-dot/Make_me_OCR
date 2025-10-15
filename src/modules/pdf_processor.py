"""PDF processing module for OCR Factory."""
import shutil
from pathlib import Path
from typing import List, Tuple
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import numpy as np


class PDFProcessor:
    """Process PDF files: split, clean, copy."""
    
    def __init__(self, logger, min_content_threshold: float = 0.05):
        """
        Initialize PDF processor.
        
        Args:
            logger: Logger instance
            min_content_threshold: Minimum content threshold for non-blank pages
        """
        self.logger = logger
        self.min_content_threshold = min_content_threshold
    
    def copy_original(self, source: Path, destination_folder: Path) -> Path:
        """
        Copy original file to destination folder.
        
        Args:
            source: Source file path
            destination_folder: Destination folder
        
        Returns:
            Path to copied file
        """
        destination_folder.mkdir(parents=True, exist_ok=True)
        destination = destination_folder / source.name
        
        shutil.copy2(source, destination)
        self.logger.info(f"Copied original: {source.name} -> {destination}")
        
        return destination
    
    def is_blank_page(self, page_image: Image.Image) -> bool:
        """
        Check if a page is blank (mostly white).
        
        Args:
            page_image: PIL Image of the page
        
        Returns:
            True if page is blank
        """
        # Convert to grayscale
        gray_image = page_image.convert('L')
        
        # Convert to numpy array
        img_array = np.array(gray_image)
        
        # Calculate the ratio of non-white pixels
        white_threshold = 250
        non_white_pixels = np.sum(img_array < white_threshold)
        total_pixels = img_array.size
        
        non_white_ratio = non_white_pixels / total_pixels
        
        return non_white_ratio < self.min_content_threshold
    
    def remove_blank_pages(self, pdf_path: Path, output_path: Path) -> Tuple[Path, int, int]:
        """
        Remove blank pages from PDF.
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
        
        Returns:
            Tuple of (output_path, original_page_count, remaining_page_count)
        """
        self.logger.info(f"Removing blank pages from: {pdf_path.name}")
        
        # Read PDF
        reader = PyPDF2.PdfReader(str(pdf_path))
        writer = PyPDF2.PdfWriter()
        
        original_pages = len(reader.pages)
        
        # Convert to images to check for blank pages
        images = convert_from_path(str(pdf_path))
        
        kept_pages = 0
        for i, (page, image) in enumerate(zip(reader.pages, images)):
            if not self.is_blank_page(image):
                writer.add_page(page)
                kept_pages += 1
                self.logger.debug(f"Keeping page {i + 1}")
            else:
                self.logger.debug(f"Removing blank page {i + 1}")
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        self.logger.info(f"Removed {original_pages - kept_pages} blank pages. "
                        f"Original: {original_pages}, Remaining: {kept_pages}")
        
        return output_path, original_pages, kept_pages
    
    def split_pdf(self, pdf_path: Path, output_folder: Path) -> List[Path]:
        """
        Split PDF into individual pages.
        
        Args:
            pdf_path: Input PDF path
            output_folder: Output folder for split pages
        
        Returns:
            List of output file paths
        """
        self.logger.info(f"Splitting PDF: {pdf_path.name}")
        
        output_folder.mkdir(parents=True, exist_ok=True)
        
        reader = PyPDF2.PdfReader(str(pdf_path))
        output_files = []
        
        base_name = pdf_path.stem
        
        for i, page in enumerate(reader.pages, start=1):
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            
            output_path = output_folder / f"{base_name}_page_{i:03d}.pdf"
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            output_files.append(output_path)
            self.logger.debug(f"Created: {output_path.name}")
        
        self.logger.info(f"Split into {len(output_files)} pages")
        
        return output_files
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """
        Get PDF metadata and information.
        
        Args:
            pdf_path: PDF file path
        
        Returns:
            Dictionary with PDF information
        """
        reader = PyPDF2.PdfReader(str(pdf_path))
        
        info = {
            'page_count': len(reader.pages),
            'metadata': reader.metadata,
            'file_size': pdf_path.stat().st_size,
            'file_name': pdf_path.name
        }
        
        return info
