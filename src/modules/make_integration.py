"""Make.com webhook integration for OCR Factory."""
import json
import requests
from typing import Dict, Optional


class MakeIntegration:
    """Integration with Make.com for workflow automation."""
    
    def __init__(self, logger, webhook_url: str = None):
        """
        Initialize Make.com integration.
        
        Args:
            logger: Logger instance
            webhook_url: Make.com webhook URL
        """
        self.logger = logger
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
        
        if self.enabled:
            self.logger.info("Make.com integration enabled")
        else:
            self.logger.info("Make.com integration disabled (no webhook URL)")
    
    def send_event(self, event_type: str, data: Dict) -> bool:
        """
        Send event to Make.com webhook.
        
        Args:
            event_type: Type of event
            data: Event data
        
        Returns:
            True if successful
        """
        if not self.enabled:
            self.logger.debug(f"Make.com webhook disabled, skipping event: {event_type}")
            return False
        
        payload = {
            'event_type': event_type,
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Sent event to Make.com: {event_type}")
                return True
            else:
                self.logger.error(f"Make.com webhook returned status {response.status_code}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending to Make.com webhook: {e}")
            return False
    
    def notify_document_processed(self, document_data: Dict) -> bool:
        """
        Notify Make.com that a document has been processed.
        
        Args:
            document_data: Document information
        
        Returns:
            True if successful
        """
        return self.send_event('document_processed', document_data)
    
    def notify_error(self, error_data: Dict) -> bool:
        """
        Notify Make.com of an error.
        
        Args:
            error_data: Error information
        
        Returns:
            True if successful
        """
        return self.send_event('processing_error', error_data)
    
    def notify_duplicate_found(self, duplicate_data: Dict) -> bool:
        """
        Notify Make.com that a duplicate was found.
        
        Args:
            duplicate_data: Duplicate information
        
        Returns:
            True if successful
        """
        return self.send_event('duplicate_found', duplicate_data)
    
    def notify_anomaly_detected(self, anomaly_data: Dict) -> bool:
        """
        Notify Make.com of detected anomalies.
        
        Args:
            anomaly_data: Anomaly information
        
        Returns:
            True if successful
        """
        return self.send_event('anomaly_detected', anomaly_data)
