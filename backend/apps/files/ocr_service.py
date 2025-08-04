"""
OCR service for processing receipts and invoices using Claude API
"""

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
import anthropic

logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR service using Claude API for receipt and invoice processing
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.CLAUDE_API_KEY
        )
        self.model = settings.CLAUDE_MODEL
    
    def process_receipt(self, image_file, document_type='receipt') -> Dict[str, Any]:
        """
        Process receipt/invoice image and extract structured data
        
        Args:
            image_file: Image file to process
            document_type: Type of document ('receipt', 'invoice')
        
        Returns:
            Dict containing extracted data and confidence score
        """
        try:
            # Prepare image for Claude API
            image_data = self._prepare_image(image_file)
            
            # Create prompt based on document type
            prompt = self._create_prompt(document_type)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_data['media_type'],
                                    "data": image_data['data']
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse response
            extracted_data = self._parse_response(response.content[0].text)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(extracted_data)
            
            return {
                'success': True,
                'data': extracted_data,
                'confidence': confidence,
                'raw_response': response.content[0].text
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'confidence': 0.0
            }
    
    def _prepare_image(self, image_file) -> Dict[str, str]:
        """
        Prepare image for Claude API
        """
        # Open and process image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (max 1568x1568 for Claude)
        max_size = 1568
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to bytes
        import io
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Encode to base64
        base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
        
        return {
            'data': base64_data,
            'media_type': 'image/jpeg'
        }
    
    def _create_prompt(self, document_type: str) -> str:
        """
        Create prompt for Claude API based on document type
        """
        if document_type == 'receipt':
            return """
Please analyze this receipt image and extract the following information in JSON format:

{
    "vendor_name": "Name of the store/vendor",
    "vendor_address": "Address of the vendor (if available)",
    "vendor_phone": "Phone number (if available)",
    "date": "Date in YYYY-MM-DD format",
    "time": "Time in HH:MM format (if available)",
    "total_amount": "Total amount as decimal number",
    "tax_amount": "Tax amount as decimal number (if available)",
    "tax_rate": "Tax rate as percentage (if available)",
    "currency": "Currency code (JPY, USD, etc.)",
    "receipt_number": "Receipt/transaction number (if available)",
    "payment_method": "Payment method (cash, card, etc.)",
    "items": [
        {
            "description": "Item description",
            "quantity": "Quantity",
            "unit_price": "Unit price",
            "total_price": "Total price for this item"
        }
    ],
    "category_suggestion": "Suggested expense category",
    "confidence_notes": "Any notes about data quality or uncertainty"
}

Please be as accurate as possible. If information is not clearly visible, use null for that field.
Focus on Japanese receipts and common formats used in Japan.
"""
        
        elif document_type == 'invoice':
            return """
Please analyze this invoice image and extract the following information in JSON format:

{
    "client_name": "Client/customer name",
    "client_address": "Client address (if available)",
    "vendor_name": "Vendor/company name",
    "vendor_address": "Vendor address (if available)",
    "invoice_number": "Invoice number",
    "date": "Invoice date in YYYY-MM-DD format",
    "due_date": "Due date in YYYY-MM-DD format (if available)",
    "total_amount": "Total amount as decimal number",
    "tax_amount": "Tax amount as decimal number (if available)",
    "tax_rate": "Tax rate as percentage (if available)",
    "currency": "Currency code (JPY, USD, etc.)",
    "payment_terms": "Payment terms (if available)",
    "items": [
        {
            "description": "Service/item description",
            "quantity": "Quantity",
            "unit_price": "Unit price",
            "total_price": "Total price for this item"
        }
    ],
    "category_suggestion": "Suggested income category",
    "confidence_notes": "Any notes about data quality or uncertainty"
}

Please be as accurate as possible. If information is not clearly visible, use null for that field.
Focus on Japanese invoices and common formats used in Japan.
"""
        
        else:
            return """
Please analyze this document image and extract any relevant financial information in JSON format.
Include fields like amounts, dates, vendor/client names, and any other relevant details.
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude API response and extract JSON data
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Clean and validate data
                return self._clean_extracted_data(data)
            else:
                # If no JSON found, try to extract key information manually
                return self._extract_fallback_data(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            return self._extract_fallback_data(response_text)
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate extracted data
        """
        cleaned_data = {}
        
        # Clean string fields
        string_fields = [
            'vendor_name', 'vendor_address', 'vendor_phone',
            'client_name', 'client_address', 'invoice_number',
            'receipt_number', 'payment_method', 'currency',
            'payment_terms', 'category_suggestion', 'confidence_notes'
        ]
        
        for field in string_fields:
            if field in data and data[field]:
                cleaned_data[field] = str(data[field]).strip()
        
        # Clean date fields
        date_fields = ['date', 'due_date']
        for field in date_fields:
            if field in data and data[field]:
                try:
                    # Try to parse and reformat date
                    date_obj = datetime.strptime(str(data[field]), '%Y-%m-%d')
                    cleaned_data[field] = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # Try other common formats
                    for fmt in ['%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            date_obj = datetime.strptime(str(data[field]), fmt)
                            cleaned_data[field] = date_obj.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
        
        # Clean time field
        if 'time' in data and data['time']:
            cleaned_data['time'] = str(data['time']).strip()
        
        # Clean numeric fields
        numeric_fields = ['total_amount', 'tax_amount', 'tax_rate']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    # Remove currency symbols and commas
                    value_str = str(data[field]).replace('¥', '').replace('$', '').replace(',', '').strip()
                    cleaned_data[field] = float(value_str)
                except (ValueError, TypeError):
                    pass
        
        # Clean items array
        if 'items' in data and isinstance(data['items'], list):
            cleaned_items = []
            for item in data['items']:
                if isinstance(item, dict):
                    cleaned_item = {}
                    if 'description' in item:
                        cleaned_item['description'] = str(item['description']).strip()
                    
                    for num_field in ['quantity', 'unit_price', 'total_price']:
                        if num_field in item and item[num_field] is not None:
                            try:
                                value_str = str(item[num_field]).replace('¥', '').replace('$', '').replace(',', '').strip()
                                cleaned_item[num_field] = float(value_str)
                            except (ValueError, TypeError):
                                pass
                    
                    if cleaned_item:
                        cleaned_items.append(cleaned_item)
            
            if cleaned_items:
                cleaned_data['items'] = cleaned_items
        
        return cleaned_data
    
    def _extract_fallback_data(self, response_text: str) -> Dict[str, Any]:
        """
        Fallback method to extract data when JSON parsing fails
        """
        # This is a simple fallback - in production, you might want more sophisticated parsing
        data = {}
        
        # Try to extract common patterns
        import re
        
        # Extract amounts (Japanese yen)
        amount_patterns = [
            r'¥([\d,]+)',
            r'(\d{1,3}(?:,\d{3})*)\s*円',
            r'合計[：:]\s*¥?([\d,]+)',
            r'total[：:]\s*¥?([\d,]+)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    data['total_amount'] = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract dates
        date_patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, response_text)
            if match:
                data['date'] = match.group(1)
                break
        
        return data
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on extracted data completeness
        """
        required_fields = ['total_amount', 'date']
        optional_fields = ['vendor_name', 'tax_amount', 'items']
        
        score = 0.0
        
        # Check required fields (60% of score)
        required_score = 0.0
        for field in required_fields:
            if field in extracted_data and extracted_data[field]:
                required_score += 1.0
        required_score = (required_score / len(required_fields)) * 0.6
        
        # Check optional fields (40% of score)
        optional_score = 0.0
        for field in optional_fields:
            if field in extracted_data and extracted_data[field]:
                optional_score += 1.0
        optional_score = (optional_score / len(optional_fields)) * 0.4
        
        score = required_score + optional_score
        
        # Adjust based on data quality indicators
        if 'confidence_notes' in extracted_data:
            notes = extracted_data['confidence_notes'].lower()
            if any(word in notes for word in ['unclear', 'uncertain', 'blurry', 'difficult']):
                score *= 0.8
        
        return min(1.0, max(0.0, score))
    
    def process_bulk_receipts(self, image_files: list) -> Dict[str, Any]:
        """
        Process multiple receipt images
        """
        results = []
        total_processed = 0
        total_successful = 0
        
        for image_file in image_files:
            result = self.process_receipt(image_file)
            results.append({
                'filename': getattr(image_file, 'name', 'unknown'),
                'result': result
            })
            
            total_processed += 1
            if result['success']:
                total_successful += 1
        
        return {
            'total_processed': total_processed,
            'total_successful': total_successful,
            'success_rate': total_successful / total_processed if total_processed > 0 else 0,
            'results': results
        }


# Singleton instance
ocr_service = OCRService()


def process_receipt_image(image_file, document_type='receipt') -> Dict[str, Any]:
    """
    Convenience function to process a single receipt image
    """
    return ocr_service.process_receipt(image_file, document_type)


def extract_financial_data(image_file) -> Tuple[Dict[str, Any], float]:
    """
    Extract financial data from image and return data with confidence score
    """
    result = ocr_service.process_receipt(image_file)
    
    if result['success']:
        return result['data'], result['confidence']
    else:
        return {}, 0.0