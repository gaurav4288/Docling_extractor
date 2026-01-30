import logging
import re
from pathlib import Path

# MARKER IMPORTS
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

logger = logging.getLogger(__name__)

class MarkerProcessor:
    def __init__(self):
        # We do NOT load models here anymore. 
        # This allows the server to start instantly.
        self.converter = None

    def _load_models(self):
        """Loads the heavy models only when needed."""
        if self.converter is None:
            logger.info("⚡ Loading Marker AI models... (First run may take time to download)")
            try:
                # Create the converter only when requested
                self.converter = PdfConverter(
                    artifact_dict=create_model_dict(),
                )
                logger.info("✅ Models loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load models: {e}")
                raise

    def process_file(self, file_path: Path) -> str:
        # 1. Ensure models are loaded before processing
        self._load_models()

        try:
            logger.info(f"Starting Marker conversion for: {file_path}")
            
            # 2. Convert
            rendered = self.converter(str(file_path))
            full_text, _, _ = text_from_rendered(rendered)
            
            # 3. Clean
            clean_text = self._clean_markdown(full_text)
            
            return clean_text

        except Exception as e:
            logger.error(f"Marker processing failed: {str(e)}")
            if "CUDA" in str(e):
                logger.error("Try setting CUDA_VISIBLE_DEVICES=-1 to force CPU mode.")
            raise RuntimeError(f"Processing failed: {str(e)}")

    def _clean_markdown(self, text: str) -> str:
        # Industry-grade cleaning
        # text = re.sub(r'GLYPH<[^>]+>', ' ', text)
        text = re.sub(r'[\u0900-\u097F]+', '', text) # Remove Hindi
        # text = re.sub(r'', '', text)
        # text = re.sub(r' +', ' ', text)
        # text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

# Singleton Instance
processor = MarkerProcessor()