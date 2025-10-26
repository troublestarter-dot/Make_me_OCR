"""Folder monitoring module for OCR Factory."""
import time
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class DocumentHandler(FileSystemEventHandler):
    """Handle file system events for documents."""
    
    def __init__(self, logger, callback: Callable, file_extensions: list = None):
        """
        Initialize document handler.
        
        Args:
            logger: Logger instance
            callback: Callback function to process files
            file_extensions: List of file extensions to monitor (e.g., ['.pdf', '.jpg'])
        """
        super().__init__()
        self.logger = logger
        self.callback = callback
        self.file_extensions = file_extensions or ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
        self.processing = set()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check file extension
        if file_path.suffix.lower() not in self.file_extensions:
            return
        
        # Avoid processing the same file multiple times
        if file_path in self.processing:
            return
        
        self.logger.info(f"New file detected: {file_path.name}")
        
        # Wait a bit to ensure file is completely written
        time.sleep(2)
        
        # Check if file still exists and is readable
        if not file_path.exists():
            self.logger.warning(f"File no longer exists: {file_path.name}")
            return
        
        try:
            # Try to open file to ensure it's not locked
            with open(file_path, 'rb') as f:
                f.read(1)
            
            self.processing.add(file_path)
            self.callback(file_path)
            self.processing.discard(file_path)
        
        except Exception as e:
            self.logger.error(f"Error accessing file {file_path.name}: {e}")


class FolderMonitor:
    """Monitor folder for new documents."""
    
    def __init__(self, logger, folder_path: Path, callback: Callable, 
                 file_extensions: list = None):
        """
        Initialize folder monitor.
        
        Args:
            logger: Logger instance
            folder_path: Path to monitor
            callback: Callback function to process files
            file_extensions: List of file extensions to monitor
        """
        self.logger = logger
        self.folder_path = folder_path
        self.callback = callback
        self.file_extensions = file_extensions
        
        self.observer = None
        self.handler = None
        
        # Ensure folder exists
        self.folder_path.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start monitoring folder."""
        self.logger.info(f"Starting folder monitor: {self.folder_path}")
        
        self.handler = DocumentHandler(
            self.logger,
            self.callback,
            self.file_extensions
        )
        
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.folder_path), recursive=False)
        self.observer.start()
        
        self.logger.info("Folder monitoring started")
    
    def stop(self):
        """Stop monitoring folder."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("Folder monitoring stopped")
    
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self.observer is not None and self.observer.is_alive()
    
    def process_existing_files(self):
        """Process files that already exist in the folder."""
        self.logger.info("Processing existing files in folder")
        
        for file_path in self.folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.file_extensions:
                self.logger.info(f"Processing existing file: {file_path.name}")
                try:
                    self.callback(file_path)
                except Exception as e:
                    self.logger.error(f"Error processing existing file {file_path.name}: {e}")
