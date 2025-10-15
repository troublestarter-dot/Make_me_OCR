"""GPT-based document analysis for OCR Factory."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI


class GPTAnalyzer:
    """GPT-powered document analysis and learning."""
    
    def __init__(self, logger, api_key: str, model: str = 'gpt-4'):
        """
        Initialize GPT analyzer.
        
        Args:
            logger: Logger instance
            api_key: OpenAI API key
            model: GPT model to use
        """
        self.logger = logger
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.error_history = []
        self.logger.info(f"GPT Analyzer initialized with model: {model}")
    
    def analyze_document(self, ocr_text: str, metadata: dict = None) -> Dict:
        """
        Analyze document content using GPT.
        
        Args:
            ocr_text: OCR extracted text
            metadata: Additional metadata
        
        Returns:
            Analysis results dictionary
        """
        self.logger.info("Analyzing document with GPT")
        
        prompt = f"""Analyze the following document and provide:
1. Document type (invoice, contract, receipt, letter, etc.)
2. Supplier/vendor name (if applicable)
3. Date (if found)
4. Key information extracted
5. Confidence score (0-1)
6. Any anomalies detected

Document text:
{ocr_text[:3000]}

Provide your analysis in JSON format with keys: document_type, supplier, date, key_info, confidence, anomalies.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert document analyzer. Analyze documents and extract structured information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            self.logger.info(f"Document analysis complete: Type={analysis.get('document_type', 'unknown')}")
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Error during document analysis: {e}")
            return {
                'document_type': 'unknown',
                'supplier': 'unknown',
                'date': None,
                'key_info': {},
                'confidence': 0.0,
                'anomalies': [str(e)]
            }
    
    def classify_supplier(self, supplier_name: str, ocr_text: str) -> Dict:
        """
        Classify and categorize supplier.
        
        Args:
            supplier_name: Supplier name
            ocr_text: Document text
        
        Returns:
            Supplier classification
        """
        self.logger.info(f"Classifying supplier: {supplier_name}")
        
        prompt = f"""Classify the following supplier:
Supplier Name: {supplier_name}

Context from document:
{ocr_text[:1000]}

Provide classification with:
1. Industry/category
2. Reliability score (0-1)
3. Common document types from this supplier
4. Any red flags or notes

Respond in JSON format with keys: industry, reliability_score, common_doc_types, notes.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in supplier classification and risk assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            classification = json.loads(response.choices[0].message.content)
            self.logger.info(f"Supplier classified: Industry={classification.get('industry', 'unknown')}")
            
            return classification
        
        except Exception as e:
            self.logger.error(f"Error classifying supplier: {e}")
            return {
                'industry': 'unknown',
                'reliability_score': 0.5,
                'common_doc_types': [],
                'notes': str(e)
            }
    
    def predict_document_type(self, text_preview: str, file_name: str) -> Dict:
        """
        Predict document type before full processing.
        
        Args:
            text_preview: Preview of document text
            file_name: File name
        
        Returns:
            Prediction results
        """
        self.logger.info("Predicting document type")
        
        prompt = f"""Based on the file name and text preview, predict the document type.

File name: {file_name}
Text preview:
{text_preview[:500]}

Predict:
1. Document type (invoice, receipt, contract, etc.)
2. Confidence (0-1)
3. Suggested processing priority (high, medium, low)

Respond in JSON format with keys: document_type, confidence, priority.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at predicting document types."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            prediction = json.loads(response.choices[0].message.content)
            self.logger.info(f"Document type predicted: {prediction.get('document_type', 'unknown')}")
            
            return prediction
        
        except Exception as e:
            self.logger.error(f"Error predicting document type: {e}")
            return {
                'document_type': 'unknown',
                'confidence': 0.0,
                'priority': 'medium'
            }
    
    def detect_anomalies(self, document_data: Dict, historical_data: List[Dict] = None) -> List[str]:
        """
        Detect anomalies in document.
        
        Args:
            document_data: Current document data
            historical_data: Historical documents for comparison
        
        Returns:
            List of detected anomalies
        """
        self.logger.info("Detecting anomalies")
        
        prompt = f"""Analyze this document for anomalies:

Current document:
{json.dumps(document_data, indent=2)}

Check for:
1. Unusual patterns
2. Missing expected information
3. Inconsistencies
4. Suspicious content
5. Format issues

List any anomalies found. Respond with JSON format with key 'anomalies' containing a list of strings.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at detecting document anomalies and fraud."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            anomalies = result.get('anomalies', [])
            
            if anomalies:
                self.logger.warning(f"Detected {len(anomalies)} anomalies")
            else:
                self.logger.info("No anomalies detected")
            
            return anomalies
        
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return [f"Error during anomaly detection: {str(e)}"]
    
    def learn_from_error(self, error_data: Dict):
        """
        Learn from processing errors.
        
        Args:
            error_data: Error information
        """
        self.error_history.append(error_data)
        self.logger.info(f"Logged error for learning: {error_data.get('error_type', 'unknown')}")
        
        # Keep only recent errors (last 100)
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
    
    def get_error_insights(self) -> Dict:
        """
        Get insights from error history.
        
        Returns:
            Error insights and recommendations
        """
        if not self.error_history:
            return {'insights': 'No errors recorded yet', 'recommendations': []}
        
        self.logger.info("Generating error insights")
        
        error_summary = json.dumps(self.error_history[-20:], indent=2)
        
        prompt = f"""Analyze these recent processing errors and provide insights:

{error_summary}

Provide:
1. Common error patterns
2. Root causes
3. Recommendations to prevent future errors

Respond in JSON format with keys: patterns, root_causes, recommendations.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing errors and providing solutions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
        
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return {'insights': str(e), 'recommendations': []}
