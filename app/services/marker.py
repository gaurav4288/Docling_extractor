import logging
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

logger = logging.getLogger(__name__)


class MarkerProcessor:
    def __init__(self):
        self.converter = None

    def _load_models(self):
        if self.converter is not None:
            return

        try:
            logger.info("⚡ Loading Marker + Surya models (lazy)")

            # Marker internally loads Surya 0.17 correctly
            self.converter = PdfConverter(artifact_dict=create_model_dict())

            logger.info("✅ Marker + Surya ready")

        except Exception as e:
            logger.exception("❌ Failed to load Marker models")
            raise RuntimeError(e)

    def process_file(
        self,
        file_path: Path,
    ) -> str:
        """Process a file and return extracted text.

        Note: Additional parameters are accepted for compatibility with the
        API but are not used by Marker internally (Marker decides its own
        extraction strategy).
        """
        self._load_models()

        rendered = self.converter(str(file_path))
        text, tables, metadata = text_from_rendered(rendered)

        return text
