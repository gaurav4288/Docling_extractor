from pathlib import Path
from app.services.processing import processor

# Example usage
if __name__ == '__main__':
    sample_pdf = Path('uploads/sample.pdf')
    if not sample_pdf.exists():
        print('Place a PDF called uploads/sample.pdf to try the example.')
    else:
        text = processor.process_file(sample_pdf)
        print('--- Extracted Text & Tables ---')
        print(text[:400])
        fields = processor.extract_fields(text)
        print('\n--- Extracted Fields ---')
        for k, v in fields.items():
            print(f'{k}: {v}')
