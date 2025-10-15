"""Google Services integration for OCR Factory."""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleServicesManager:
    """Manage Google Sheets and Drive operations."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, logger, service_account_file: str, 
                 sheets_id: str = None, drive_folder_id: str = None):
        """
        Initialize Google Services manager.
        
        Args:
            logger: Logger instance
            service_account_file: Path to service account JSON file
            sheets_id: Google Sheets ID
            drive_folder_id: Google Drive folder ID
        """
        self.logger = logger
        self.service_account_file = service_account_file
        self.sheets_id = sheets_id
        self.drive_folder_id = drive_folder_id
        
        self._setup_credentials()
        self._setup_sheets()
        self._setup_drive()
    
    def _setup_credentials(self):
        """Setup Google credentials."""
        self.credentials = Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.SCOPES
        )
        self.logger.info("Google credentials initialized")
    
    def _setup_sheets(self):
        """Setup Google Sheets client."""
        self.sheets_client = gspread.authorize(self.credentials)
        
        if self.sheets_id:
            try:
                self.sheet = self.sheets_client.open_by_key(self.sheets_id)
                self.logger.info(f"Connected to Google Sheet: {self.sheet.title}")
            except Exception as e:
                self.logger.error(f"Error connecting to Google Sheet: {e}")
                self.sheet = None
        else:
            self.sheet = None
    
    def _setup_drive(self):
        """Setup Google Drive client."""
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.logger.info("Google Drive service initialized")
    
    def append_to_sheet(self, worksheet_name: str, row_data: List) -> bool:
        """
        Append row to Google Sheet.
        
        Args:
            worksheet_name: Name of the worksheet
            row_data: List of values to append
        
        Returns:
            True if successful
        """
        if not self.sheet:
            self.logger.error("Google Sheet not configured")
            return False
        
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            worksheet.append_row(row_data)
            self.logger.info(f"Appended row to sheet: {worksheet_name}")
            return True
        
        except gspread.WorksheetNotFound:
            # Create worksheet if it doesn't exist
            worksheet = self.sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            worksheet.append_row(row_data)
            self.logger.info(f"Created and appended to new sheet: {worksheet_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error appending to sheet: {e}")
            return False
    
    def add_document_to_index(self, document_data: Dict) -> bool:
        """
        Add document to index sheet.
        
        Args:
            document_data: Dictionary with document information
        
        Returns:
            True if successful
        """
        row_data = [
            document_data.get('document_id', ''),
            document_data.get('file_name', ''),
            document_data.get('timestamp', datetime.now().isoformat()),
            document_data.get('page_count', ''),
            document_data.get('file_size', ''),
            document_data.get('ocr_status', 'pending'),
            document_data.get('supplier', ''),
            document_data.get('document_type', ''),
            document_data.get('duplicate', 'false'),
            document_data.get('drive_link', ''),
            document_data.get('notes', '')
        ]
        
        return self.append_to_sheet('Document Index', row_data)
    
    def add_error_log(self, error_data: Dict) -> bool:
        """
        Add error to error log sheet.
        
        Args:
            error_data: Dictionary with error information
        
        Returns:
            True if successful
        """
        row_data = [
            datetime.now().isoformat(),
            error_data.get('document_id', ''),
            error_data.get('error_type', ''),
            error_data.get('error_message', ''),
            error_data.get('processing_stage', ''),
            error_data.get('resolution', '')
        ]
        
        return self.append_to_sheet('Error Log', row_data)
    
    def upload_to_drive(self, file_path: Path, folder_id: str = None) -> Optional[str]:
        """
        Upload file to Google Drive.
        
        Args:
            file_path: Path to file
            folder_id: Folder ID (uses default if not provided)
        
        Returns:
            File ID if successful, None otherwise
        """
        folder_id = folder_id or self.drive_folder_id
        
        if not folder_id:
            self.logger.error("Google Drive folder ID not configured")
            return None
        
        try:
            file_metadata = {
                'name': file_path.name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(str(file_path), resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            
            self.logger.info(f"Uploaded to Drive: {file_path.name} (ID: {file_id})")
            
            return web_link
        
        except Exception as e:
            self.logger.error(f"Error uploading to Drive: {e}")
            return None
    
    def create_index_headers(self):
        """Create headers for index sheet if they don't exist."""
        if not self.sheet:
            return
        
        try:
            # Document Index headers
            doc_headers = [
                'Document ID', 'File Name', 'Timestamp', 'Page Count', 
                'File Size', 'OCR Status', 'Supplier', 'Document Type',
                'Duplicate', 'Drive Link', 'Notes'
            ]
            
            try:
                worksheet = self.sheet.worksheet('Document Index')
            except gspread.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(title='Document Index', rows=1000, cols=20)
            
            # Check if headers exist
            if not worksheet.row_values(1):
                worksheet.append_row(doc_headers)
                self.logger.info("Created Document Index headers")
            
            # Error Log headers
            error_headers = [
                'Timestamp', 'Document ID', 'Error Type', 
                'Error Message', 'Processing Stage', 'Resolution'
            ]
            
            try:
                error_worksheet = self.sheet.worksheet('Error Log')
            except gspread.WorksheetNotFound:
                error_worksheet = self.sheet.add_worksheet(title='Error Log', rows=1000, cols=10)
            
            if not error_worksheet.row_values(1):
                error_worksheet.append_row(error_headers)
                self.logger.info("Created Error Log headers")
        
        except Exception as e:
            self.logger.error(f"Error creating headers: {e}")
