"""CloudConvert OCR integration for OCR Factory."""
import time
from pathlib import Path
from typing import Optional
import cloudconvert


class OCRService:
    """CloudConvert OCR service."""
    
    def __init__(self, logger, api_key: str):
        """
        Initialize OCR service.
        
        Args:
            logger: Logger instance
            api_key: CloudConvert API key
        """
        self.logger = logger
        self.api_key = api_key
        self.client = cloudconvert.CloudConvert(api_key=api_key)
        self.logger.info("CloudConvert OCR service initialized")
    
    def ocr_pdf(self, input_path: Path, output_path: Path, 
                language: str = 'eng') -> Optional[Path]:
        """
        Perform OCR on PDF file.
        
        Args:
            input_path: Input PDF path
            output_path: Output PDF path (with text layer)
            language: OCR language code
        
        Returns:
            Output path if successful, None otherwise
        """
        self.logger.info(f"Starting OCR for: {input_path.name}")
        
        try:
            # Create OCR job
            job = self.client.Job.create(payload={
                'tasks': {
                    'import-my-file': {
                        'operation': 'import/upload'
                    },
                    'ocr-my-file': {
                        'operation': 'ocr',
                        'input': 'import-my-file',
                        'language': language,
                        'output_format': 'pdf'
                    },
                    'export-my-file': {
                        'operation': 'export/url',
                        'input': 'ocr-my-file'
                    }
                }
            })
            
            # Upload file
            upload_task = job['tasks'][0]
            self.client.Task.upload(
                file_name=input_path.name,
                task=upload_task,
                file=open(input_path, 'rb')
            )
            
            # Wait for job completion
            job = self.client.Job.wait(id=job['id'])
            
            # Download result
            for task in job['tasks']:
                if task.get('name') == 'export-my-file' and task.get('status') == 'finished':
                    file_url = task['result']['files'][0]['url']
                    
                    # Download the file
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    self.client.download(url=file_url, file_path=str(output_path))
                    
                    self.logger.info(f"OCR completed: {output_path.name}")
                    return output_path
            
            self.logger.error(f"OCR job did not complete successfully for: {input_path.name}")
            return None
        
        except Exception as e:
            self.logger.error(f"Error during OCR: {e}")
            return None
    
    def ocr_image(self, input_path: Path, output_path: Path, 
                  language: str = 'eng') -> Optional[Path]:
        """
        Perform OCR on image file.
        
        Args:
            input_path: Input image path
            output_path: Output PDF path
            language: OCR language code
        
        Returns:
            Output path if successful, None otherwise
        """
        self.logger.info(f"Starting OCR for image: {input_path.name}")
        
        try:
            job = self.client.Job.create(payload={
                'tasks': {
                    'import-my-file': {
                        'operation': 'import/upload'
                    },
                    'ocr-my-file': {
                        'operation': 'ocr',
                        'input': 'import-my-file',
                        'language': language,
                        'output_format': 'pdf'
                    },
                    'export-my-file': {
                        'operation': 'export/url',
                        'input': 'ocr-my-file'
                    }
                }
            })
            
            upload_task = job['tasks'][0]
            self.client.Task.upload(
                file_name=input_path.name,
                task=upload_task,
                file=open(input_path, 'rb')
            )
            
            job = self.client.Job.wait(id=job['id'])
            
            for task in job['tasks']:
                if task.get('name') == 'export-my-file' and task.get('status') == 'finished':
                    file_url = task['result']['files'][0]['url']
                    
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    self.client.download(url=file_url, file_path=str(output_path))
                    
                    self.logger.info(f"OCR completed for image: {output_path.name}")
                    return output_path
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error during image OCR: {e}")
            return None
    
    def get_usage(self) -> dict:
        """
        Get API usage statistics.
        
        Returns:
            Dictionary with usage information
        """
        try:
            user = self.client.User.me()
            return {
                'credits': user.get('credits', 0),
                'username': user.get('username', ''),
            }
        except Exception as e:
            self.logger.error(f"Error getting usage: {e}")
            return {}
