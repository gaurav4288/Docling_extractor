# Marker Convert FastAPI

Simple single-endpoint FastAPI service that accepts a single file (PDF, image, or DOCX) and returns a downloadable Markdown (.md) file produced by Marker.

## Endpoints

- POST /convert
  - form field: `file` (multipart/form-data)
  - returns: Markdown file as an attachment (`converted.md`)

## Quickstart (local)

### Python version and system dependencies ⚠️

- This project recommends **Python 3.9.x** on Windows. Some packages (notably `unstructured` -> `numba`) are not compatible with Python >= 3.10 and will fail to build on Python 3.12.
- Install **Tesseract OCR** and **Poppler** on Windows and ensure their `bin` folders are added to `PATH`:
  - Tesseract: https://github.com/tesseract-ocr/tesseract
  - Poppler: https://github.com/oschwartz10612/poppler-windows
- Optional: if you need HEIF/HEIC image support (some PDFs embed HEIF images), install `pi-heif` or `pillow-heif`:
  - `pip install pi-heif` or `pip install pillow-heif`
- Note: The `unstructured` package may require an additional package (`unstructured-inference`) for layout/high-res partitioning and model-backed inference. If you see "No module named 'unstructured_inference'" install it with:
  - `pip install unstructured-inference`
  - Or use conda-forge if you prefer prebuilt packages: `conda install -c conda-forge unstructured-inference`

### Create virtual environment and install (Windows PowerShell)

```powershell
# Use a Python 3.9 interpreter (adjust path if needed)
py -3.9 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2. Run server:

```bash
uvicorn app:app --reload --port 8000
```

3. Example cURL (save output as `converted.md`):

```bash
curl -X POST "http://localhost:8000/convert" \
  -H "accept: */*" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf" \
  -o converted.md
```

## Docker

Build and run:

```bash
docker build -t marker-convert .
docker run -p 8000:8000 marker-convert
```

## Notes

- Supported file types: PDF, PNG, JPG/JPEG, TIFF, DOCX
- Conversion is done locally using the `marker` package (no external service required)
- For large files or heavy workloads, consider running behind a production server or queueing conversions
