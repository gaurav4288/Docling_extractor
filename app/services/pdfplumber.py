import logging
import re
from pathlib import Path
import pdfplumber
from tabulate import tabulate

logger = logging.getLogger(__name__)


class FormProcessor:
    def process_file(self, file_path: Path) -> str:
        logger.info(f"Processing with pdfplumber: {file_path}")
        full_output = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # 1. FIND TABLES
                    # We locate the tables first to get their coordinates (Bounding Boxes)
                    tables_obj = page.find_tables(
                        table_settings={
                            "vertical_strategy": "lines",
                            "horizontal_strategy": "lines",
                            "intersection_y_tolerance": 10,
                        }
                    )

                    # 2. EXTRACT & FORMAT TABLES
                    if tables_obj:
                        for table in tables_obj:
                            # Extract the raw data
                            raw_data = table.extract()
                            if not raw_data:
                                continue

                            # Clean the table data
                            clean_data = []
                            for row in raw_data:
                                # Clean each cell (remove Hindi/Garbage)
                                clean_row = [self._clean_cell(cell) for cell in row]
                                # Only add non-empty rows
                                if any(clean_row):
                                    clean_data.append(clean_row)

                            # Format as a Grid
                            if clean_data:
                                table_txt = tabulate(
                                    clean_data, tablefmt="grid", maxcolwidths=[40, 40]
                                )
                                full_output.append(table_txt)

                    # 3. EXTRACT NARRATIVE TEXT (Excluding Tables)
                    # We create a filter function to ignore text inside the tables we just found.
                    # This prevents Duplicate content.

                    def not_inside_tables(obj):
                        # obj is a dictionary with keys: x0, top, x1, bottom
                        obj_x = (obj["x0"] + obj["x1"]) / 2
                        obj_y = (obj["top"] + obj["bottom"]) / 2

                        for t in tables_obj:
                            # Check if the text center is inside the table bbox
                            bbox = t.bbox  # (x0, top, x1, bottom)
                            if (bbox[0] <= obj_x <= bbox[2]) and (
                                bbox[1] <= obj_y <= bbox[3]
                            ):
                                return False  # It IS inside a table, so ignore it
                        return True  # It is NOT inside a table, keep it

                    # Filter the page
                    filtered_page = page.filter(not_inside_tables)

                    # Extract the remaining text (Headers, Terms, Footers)
                    raw_text = filtered_page.extract_text()

                    if raw_text:
                        # Clean the narrative text line-by-line
                        clean_narrative = self._clean_narrative_text(raw_text)
                        full_output.append(clean_narrative)

            return "\n\n".join(full_output)

        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise RuntimeError(f"Processing failed: {str(e)}")

    def _clean_cell(self, cell):
        """Cleans Table Cells (GeM Format: 'Hindi / English')"""
        if not cell:
            return ""
        text = cell.replace("\n", " ").strip()
        return self._pick_english_part(text)

    def _clean_narrative_text(self, text_block):
        """Cleans Narrative Text (Terms & Conditions)"""
        lines = text_block.split("\n")
        clean_lines = []
        for line in lines:
            cleaned = self._pick_english_part(line)
            if cleaned and len(cleaned) > 2:  # Ignore tiny noise
                clean_lines.append(cleaned)
        return "\n".join(clean_lines)

    def _pick_english_part(self, text):
        """
        Core Logic: Splits 'Garbage / Meaningful Text' and returns the English part.
        """
        if not text:
            return ""

        # 1. If line contains '/', split it.
        if "/" in text:
            parts = text.split("/")
            # Heuristic: The English part usually has more Capital Letters or standard ASCII
            # We pick the segment with the most ASCII letters
            best_part = max(
                parts, key=lambda x: len([c for c in x if c.isascii() and c.isalnum()])
            )
            text = best_part

        # 2. Remove Specific GeM Artifacts
        text = re.sub(r"\(cid:[0-9]+\)", "", text)  # Remove (cid:123) errors
        text = re.sub(r"GLYPH<[^>]+>", "", text)  # Remove GLYPH tags

        # 3. Remove non-ASCII characters (Hindi scripts often fall here)
        # This keeps English, Numbers, and Punctuation.
        text = re.sub(r"[^\x00-\x7F]+", "", text)

        return text.strip()
