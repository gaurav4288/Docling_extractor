from pathlib import Path
import os
import logging

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice

# IMPORT SURYA OPTIONS
from docling_surya import SuryaOcrOptions 

logger = logging.getLogger(__name__)

class DoclingService:
    def __init__(self):
        self.converter = None

    def process_file(self, file_path: Path) -> str:
        """Process a saved file using Docling + Surya OCR."""
        input_path = Path(file_path)

        # 1. SETUP SURYA OPTIONS
        # Surya detects languages automatically, but hints help performance.
        ocr_options = SuryaOcrOptions(
            lang=["hi", "en"],
        )

        # 2. CONFIGURE PIPELINE
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            force_ocr=True,             # Forces OCR on all pages
            ocr_options=ocr_options,    # Pass the Surya options here
            do_table_structure=True,
            allow_external_plugins=True,
            
            # Important: Surya is heavy, so configure the accelerator (GPU)
            accelerator_options=AcceleratorOptions(
                num_threads=4, 
                device=AcceleratorDevice.CUDA if os.getenv("USE_CUDA") == "1" else AcceleratorDevice.AUTO
            ),
        )

        # 3. CREATE CONVERTER
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )

        # 4. CONVERT
        # The first time this runs, it will download Surya models (~300MB)
        result = converter.convert(input_path)
        markdown = result.document.export_to_markdown()

        return {"markdown": markdown}