"""Main orchestrator for OCR Factory."""
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.modules.logger import setup_logger
from src.modules.folder_monitor import FolderMonitor
from src.modules.pdf_processor import PDFProcessor
from src.modules.document_id import DocumentIDGenerator
from src.modules.duplicate_checker import DuplicateChecker
from src.modules.google_services import GoogleServicesManager
from src.modules.ocr_service import OCRService
from src.modules.gpt_analyzer import GPTAnalyzer
from src.modules.make_integration import MakeIntegration


class OCRFactory:
    """Main OCR Factory orchestrator."""
    
    def __init__(self):
        """Initialize OCR Factory."""
        # Setup logging
        self.logger = setup_logger('OCRFactory', Config.LOG_FILE, Config.LOG_LEVEL)
        self.logger.info("=" * 80)
        self.logger.info("OCR FACTORY STARTING")
        self.logger.info("=" * 80)
        
        # Validate configuration
        try:
            Config.validate()
            self.logger.info("Configuration validated successfully")
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            self.logger.warning("Starting in limited mode (some features may not work)")
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components."""
        self.logger.info("Initializing components...")
        
        # PDF Processor
        self.pdf_processor = PDFProcessor(
            self.logger,
            Config.MIN_PAGE_CONTENT_THRESHOLD
        )
        
        # Document ID Generator
        self.id_generator = DocumentIDGenerator()
        
        # Duplicate Checker
        self.duplicate_checker = DuplicateChecker(
            self.logger,
            Config.INDEX_FOLDER,
            Config.DUPLICATE_SIMILARITY_THRESHOLD
        )
        
        # Google Services
        if Config.GOOGLE_SERVICE_ACCOUNT_FILE and Path(Config.GOOGLE_SERVICE_ACCOUNT_FILE).exists():
            try:
                self.google_services = GoogleServicesManager(
                    self.logger,
                    Config.GOOGLE_SERVICE_ACCOUNT_FILE,
                    Config.GOOGLE_SHEETS_ID,
                    Config.GOOGLE_DRIVE_FOLDER_ID
                )
                self.google_services.create_index_headers()
            except Exception as e:
                self.logger.error(f"Failed to initialize Google Services: {e}")
                self.google_services = None
        else:
            self.logger.warning("Google Services not configured")
            self.google_services = None
        
        # OCR Service
        if Config.CLOUDCONVERT_API_KEY:
            try:
                self.ocr_service = OCRService(
                    self.logger,
                    Config.CLOUDCONVERT_API_KEY
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize OCR Service: {e}")
                self.ocr_service = None
        else:
            self.logger.warning("OCR Service not configured")
            self.ocr_service = None
        
        # GPT Analyzer
        if Config.OPENAI_API_KEY:
            try:
                self.gpt_analyzer = GPTAnalyzer(
                    self.logger,
                    Config.OPENAI_API_KEY,
                    Config.OPENAI_MODEL
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize GPT Analyzer: {e}")
                self.gpt_analyzer = None
        else:
            self.logger.warning("GPT Analyzer not configured")
            self.gpt_analyzer = None
        
        # Make.com Integration
        self.make_integration = MakeIntegration(
            self.logger,
            Config.MAKE_WEBHOOK_URL
        )
        
        self.logger.info("Components initialized")
    
    def process_document(self, file_path: Path):
        """
        Process a single document through the entire pipeline.
        
        Args:
            file_path: Path to document file
        """
        self.logger.info("=" * 80)
        self.logger.info(f"PROCESSING DOCUMENT: {file_path.name}")
        self.logger.info("=" * 80)
        
        document_data = {
            'file_name': file_path.name,
            'timestamp': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        try:
            # Step 1: Generate Document ID
            document_id = self.id_generator.generate_composite_id(file_path)
            document_data['document_id'] = document_id
            self.logger.info(f"Generated Document ID: {document_id}")
            
            # Step 2: Copy Original
            original_path = self.pdf_processor.copy_original(
                file_path,
                Config.ORIGINALS_FOLDER
            )
            document_data['original_path'] = str(original_path)
            
            # Step 3: Check for Duplicates
            document_hash = self.duplicate_checker.calculate_hash(file_path)
            duplicates = self.duplicate_checker.find_duplicates(file_path, document_hash)
            
            if duplicates:
                self.logger.warning(f"DUPLICATE DETECTED: {len(duplicates)} match(es) found")
                document_data['duplicate'] = True
                document_data['duplicate_matches'] = duplicates
                
                # Notify Make.com
                self.make_integration.notify_duplicate_found(document_data)
                
                # Still process but mark as duplicate
            else:
                document_data['duplicate'] = False
            
            # Step 4: Get PDF Info
            pdf_info = self.pdf_processor.get_pdf_info(file_path)
            document_data.update(pdf_info)
            
            # Step 5: Remove Blank Pages
            cleaned_path = Config.OUTPUT_FOLDER / f"cleaned_{file_path.name}"
            cleaned_path, original_pages, kept_pages = self.pdf_processor.remove_blank_pages(
                file_path,
                cleaned_path
            )
            document_data['original_pages'] = original_pages
            document_data['cleaned_pages'] = kept_pages
            
            # Step 6: Split PDF (optional, based on page count)
            if kept_pages > 1:
                split_folder = Config.OUTPUT_FOLDER / f"split_{file_path.stem}"
                split_files = self.pdf_processor.split_pdf(cleaned_path, split_folder)
                document_data['split_files'] = [str(f) for f in split_files]
                self.logger.info(f"Split into {len(split_files)} files")
            else:
                document_data['split_files'] = []
            
            # Step 7: Perform OCR
            if self.ocr_service:
                ocr_output_path = Config.OUTPUT_FOLDER / f"ocr_{file_path.name}"
                ocr_result = self.ocr_service.ocr_pdf(cleaned_path, ocr_output_path)
                
                if ocr_result:
                    document_data['ocr_status'] = 'completed'
                    document_data['ocr_path'] = str(ocr_result)
                    self.logger.info("OCR completed successfully")
                else:
                    document_data['ocr_status'] = 'failed'
                    self.logger.error("OCR failed")
            else:
                document_data['ocr_status'] = 'skipped'
                self.logger.info("OCR skipped (service not configured)")
            
            # Step 8: GPT Analysis
            if self.gpt_analyzer and document_data.get('ocr_status') == 'completed':
                # Read OCR text (simplified - in real scenario, extract text from PDF)
                analysis = self.gpt_analyzer.analyze_document(
                    f"Document: {file_path.name}",  # Simplified
                    document_data
                )
                document_data['gpt_analysis'] = analysis
                
                # Classify supplier if detected
                if analysis.get('supplier'):
                    supplier_classification = self.gpt_analyzer.classify_supplier(
                        analysis['supplier'],
                        f"Document: {file_path.name}"
                    )
                    document_data['supplier_classification'] = supplier_classification
                
                # Detect anomalies
                anomalies = self.gpt_analyzer.detect_anomalies(document_data)
                document_data['anomalies'] = anomalies
                
                if anomalies:
                    self.make_integration.notify_anomaly_detected({
                        'document_id': document_id,
                        'anomalies': anomalies
                    })
            
            # Step 9: Upload to Google Drive
            if self.google_services:
                drive_link = self.google_services.upload_to_drive(original_path)
                if drive_link:
                    document_data['drive_link'] = drive_link
            
            # Step 10: Add to Index
            self.duplicate_checker.add_to_index(
                document_id,
                file_path,
                document_hash,
                document_data
            )
            
            # Step 11: Add to Google Sheets
            if self.google_services:
                self.google_services.add_document_to_index(document_data)
            
            # Step 12: Notify Make.com
            document_data['status'] = 'completed'
            self.make_integration.notify_document_processed(document_data)
            
            self.logger.info(f"DOCUMENT PROCESSING COMPLETED: {document_id}")
        
        except Exception as e:
            self.logger.error(f"ERROR PROCESSING DOCUMENT: {e}", exc_info=True)
            
            error_data = {
                'document_id': document_data.get('document_id', 'unknown'),
                'file_name': file_path.name,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'processing_stage': 'unknown',
                'timestamp': datetime.now().isoformat()
            }
            
            # Log error to Google Sheets
            if self.google_services:
                self.google_services.add_error_log(error_data)
            
            # Learn from error
            if self.gpt_analyzer:
                self.gpt_analyzer.learn_from_error(error_data)
            
            # Notify Make.com
            self.make_integration.notify_error(error_data)
    
    def start_monitoring(self):
        """Start folder monitoring."""
        self.logger.info("Setting up folder monitoring...")
        
        # Process existing files first
        self.monitor = FolderMonitor(
            self.logger,
            Config.INPUT_FOLDER,
            self.process_document,
            file_extensions=['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
        )
        
        self.logger.info("Processing existing files...")
        self.monitor.process_existing_files()
        
        self.logger.info("Starting real-time monitoring...")
        self.monitor.start()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.monitor.stop()
            self.logger.info("OCR Factory stopped")
    
    def run(self):
        """Run the OCR Factory."""
        try:
            self.start_monitoring()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point."""
    factory = OCRFactory()
    factory.run()


if __name__ == '__main__':
    main()
