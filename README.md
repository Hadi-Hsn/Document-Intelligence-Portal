# Document Intelligence Portal

AI-powered document analysis portal built with **Streamlit** and **OpenAI GPT-4o**.  
Upload contracts, legal documents, and other files for automatic text extraction, metadata detection, and risk analysis.

## Features

- **Multi-format upload**: PDF, DOCX, DOC, PNG, JPG, TIFF, and more
- **Smart text extraction**: Embedded text + OCR for scanned documents
- **AI-powered analysis** via OpenAI GPT-4o:
  - Document summarization
  - Contract metadata extraction (parties, dates, jurisdiction, payment terms, etc.)
  - Risk and alert detection with severity levels
  - Key clause highlighting
- **Clean, professional UI** with tabbed results view

## Prerequisites

- **Python 3.10+**
- **Tesseract OCR** (required for scanned PDFs and image files)

### Install Tesseract OCR

**Windows:**

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH (default: `C:\Program Files\Tesseract-OCR`)
3. Verify: `tesseract --version`

**macOS:**

```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install tesseract-ocr
```

## Setup

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your OpenAI API key:**

   Edit the `.env` file and replace the placeholder:

   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

   Or enter it directly in the sidebar of the app.

3. **Run the application:**

   ```bash
   streamlit run app.py
   ```

4. **Open in browser:**  
   The app will open at `http://localhost:8501`

## Project Structure

```
├── app.py              # Streamlit UI application
├── extractors.py       # Text extraction (PDF, DOCX, images, OCR)
├── analyzer.py         # OpenAI document analysis
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (API key)
└── README.md           # This file
```

## Usage

1. Open the app in your browser
2. (Optional) Enter your OpenAI API key in the sidebar
3. Upload one or more documents using the file uploader
4. Wait for text extraction and AI analysis to complete
5. Browse results across tabs: Summary, Metadata, Risks, Key Clauses, Full Text

## Notes

- Large documents are truncated to 100,000 characters for analysis
- OCR quality depends on image resolution and Tesseract installation
- `.doc` files (old Word format) require the file to actually be `.docx` internally
- The app uses GPT-4o for analysis; ensure your API key has access to this model
