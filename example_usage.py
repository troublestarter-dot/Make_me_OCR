"""Example usage of OCR Factory components."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.modules.logger import setup_logger
from src.modules.document_id import DocumentIDGenerator
from src.modules.duplicate_checker import DuplicateChecker
from src.modules.pdf_processor import PDFProcessor


def example_document_id():
    """Example: Generate document IDs."""
    print("\n=== Document ID Generation Examples ===\n")
    
    generator = DocumentIDGenerator()
    
    # UUID-based
    uuid_id = generator.generate_uuid()
    print(f"UUID ID: {uuid_id}")
    
    # Timestamp-based
    timestamp_id = generator.generate_timestamp_id()
    print(f"Timestamp ID: {timestamp_id}")
    
    # If you have a file:
    # file_path = Path("sample.pdf")
    # hash_id = generator.generate_hash_id(file_path)
    # composite_id = generator.generate_composite_id(file_path)
    # print(f"Hash ID: {hash_id}")
    # print(f"Composite ID: {composite_id}")


def example_logger():
    """Example: Using the logger."""
    print("\n=== Logger Example ===\n")
    
    logger = setup_logger('ExampleLogger', level='INFO')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


def example_pdf_processor():
    """Example: PDF processing."""
    print("\n=== PDF Processor Example ===\n")
    
    logger = setup_logger('PDFProcessor', level='INFO')
    processor = PDFProcessor(logger, min_content_threshold=0.05)
    
    print("PDF Processor initialized")
    print("Features:")
    print("  - Copy originals")
    print("  - Remove blank pages")
    print("  - Split PDFs")
    print("  - Get PDF info")
    print("\nTo use: processor.remove_blank_pages(input_path, output_path)")


def example_duplicate_checker():
    """Example: Duplicate checking."""
    print("\n=== Duplicate Checker Example ===\n")
    
    logger = setup_logger('DuplicateChecker', level='INFO')
    checker = DuplicateChecker(
        logger,
        Config.INDEX_FOLDER,
        similarity_threshold=0.95
    )
    
    print("Duplicate Checker initialized")
    print(f"Index folder: {Config.INDEX_FOLDER}")
    print(f"Similarity threshold: 0.95")
    print("\nTo use: checker.check_duplicate(file_path)")


def example_config():
    """Example: Configuration."""
    print("\n=== Configuration Example ===\n")
    
    print(f"Input Folder: {Config.INPUT_FOLDER}")
    print(f"Output Folder: {Config.OUTPUT_FOLDER}")
    print(f"Originals Folder: {Config.ORIGINALS_FOLDER}")
    print(f"Index Folder: {Config.INDEX_FOLDER}")
    print(f"Log Level: {Config.LOG_LEVEL}")
    print(f"Log File: {Config.LOG_FILE}")
    print(f"OpenAI Model: {Config.OPENAI_MODEL}")
    print(f"Min Content Threshold: {Config.MIN_PAGE_CONTENT_THRESHOLD}")
    print(f"Duplicate Threshold: {Config.DUPLICATE_SIMILARITY_THRESHOLD}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("OCR FACTORY - USAGE EXAMPLES")
    print("=" * 60)
    
    example_config()
    example_logger()
    example_document_id()
    example_pdf_processor()
    example_duplicate_checker()
    
    print("\n" + "=" * 60)
    print("To start the full OCR Factory, run: python src/main.py")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
