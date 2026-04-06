"""
Tax Document Processor - Extract data from payslips, invoices using Ollama

Supports: PDF, JPG, PNG
Uses local AI (codellama:7b) for privacy
"""

import json
import ollama
from pathlib import Path
from typing import Dict, Any, List


class TaxDocumentProcessor:
    EXTRACTION_PROMPT = """You are a UK tax document specialist. Extract all financial data.

Return STRICTLY valid JSON with this exact structure:

{
  "document_type": "payslip|p60|p45|invoice|receipt|unknown",
  "confidence": 0.95,
  "period": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"},
  "issuer": "Company Name",
  "financial_data": {
    "gross_income": 0.0,
    "tax_deducted": 0.0,
    "ni_employee": 0.0,
    "ni_employer": 0.0,
    "pension_contributions": 0.0,
    "tax_code": "",
    "national_insurance_category": ""
  },
  "employee_or_customer": {
    "name": "",
    "ni_number": "",
    "utr": ""
  }
}

Only return JSON, nothing else.

Document content:
{text}
"""

    def __init__(self, model: str = "codellama:7b"):
        self.model = model
        try:
            self.client = ollama.Client(host='http://localhost:11434')
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            self.client = None

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process document and extract structured data"""
        path = Path(file_path)
        if not path.exists():
            return {'document_type': 'error', 'error': 'File not found'}

        # Extract text (simplified - for PDFs use PyPDF2 in production)
        try:
            if path.suffix.lower() == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                text = self._extract_image_text(file_path)
            else:
                return {'document_type': 'error', 'error': 'Unsupported file type'}
        except Exception as e:
            return {'document_type': 'error', 'error': f'Text extraction failed: {e}'}

        if not self.client:
            return {'document_type': 'error', 'error': 'Ollama not available'}

        # Call AI
        prompt = self.EXTRACTION_PROMPT.format(text=text[:8000])
        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            extracted = response['response']

            # Extract JSON
            json_start = extracted.find('{')
            json_end = extracted.rfind('}') + 1
            json_str = extracted[json_start:json_end]
            data = json.loads(json_str)

            data['_meta'] = {
                'source_file': path.name,
                'model_used': self.model,
                'processed_at': datetime.now().isoformat()
            }
            return data
        except Exception as e:
            return {'document_type': 'error', 'error': f'AI extraction failed: {e}'}

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            import pymupdf
            doc = pymupdf.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            # Fallback
            return "PDF text extraction requires pymupdf. Install: pip install pymupdf"

    def _extract_image_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(image_path)
            return pytesseract.image_to_string(image)
        except ImportError:
            return "OCR requires pytesseract and pillow. Install: pip install pytesseract pillow"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tax Document Processor")
    parser.add_argument('file', help='Path to document')
    parser.add_argument('--model', default='codellama:7b')
    parser.add_argument('--output', help='Save JSON to file')

    args = parser.parse_args()
    processor = TaxDocumentProcessor(model=args.model)
    result = processor.process_file(args.file)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
