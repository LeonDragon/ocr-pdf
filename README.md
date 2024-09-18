
# Flask OCR Application with Google Cloud Vision API

This project is a Flask web application that allows users to upload PDF files, converts the pages to images, performs Optical Character Recognition (OCR) using the Google Cloud Vision API, and returns a PDF file with the extracted text. This application supports Vietnamese characters using the `DejaVuSans` font.

## Features

- PDF to image conversion using `pdf2image` and Poppler.
- OCR using Google Cloud Vision API.
- Text extraction and formatting into a downloadable PDF.
- Multi-page PDFs are supported, with configurable pages per image.

## Prerequisites

- **Operating System**: Windows 10/11
- **Python Version**: 3.x
- **Google Cloud Project**: Enable Google Cloud Vision API.

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/flask-ocr-app.git
cd flask-ocr-app
```

### Step 2: Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
```

### Step 3: Install Required Python Libraries

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes the following:

```
Flask
pdf2image
google-cloud-vision
Pillow
reportlab
werkzeug
```

### Step 4: Install Poppler

Poppler is required to convert PDF files to images.

1. Download Poppler for Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Extract the downloaded file and note the installation path (e.g., `C:\Program Files\poppler\Library\bin`).
3. Add Poppler’s `bin` directory to your system `PATH`.

### Step 5: Set Up Google Cloud Vision API

1. Create a Google Cloud project and enable the [Google Cloud Vision API](https://cloud.google.com/vision).
2. Create a service account and download the JSON key file.
3. Place the JSON key file in the `secrets/` directory (you may need to create this directory).
4. Update the environment variable in your code to point to the key file:

```python
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/ocr_gcp_api_key.json'
```

### Step 6: Font Configuration

To support Vietnamese characters, the app uses the `DejaVuSans.ttf` font. Ensure that this font file is located in your project directory. You can download it from [DejaVu Fonts](https://dejavu-fonts.github.io/).

### Step 7: Run the Application

```bash
python app.py
```

Navigate to `http://127.0.0.1:5000` in your browser to access the web interface.

### Step 8: Upload and Process PDF

1. Upload a PDF file.
2. The application will process the PDF, extract the text using Google Cloud Vision OCR, and allow you to download the extracted text as a PDF.

## Project Structure

```
flask-ocr-app/
│
├── app.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # HTML template for the web page
├── uploads/                # Directory for uploaded files (auto-created)
├── secrets/
│   └── ocr_gcp_api_key.json # Google Cloud API credentials
└── DejaVuSans.ttf          # Font file for supporting Vietnamese characters
```

## Code Overview

### Key Functions

- **`allowed_file(filename)`**: Validates file type (PDF).
- **`ocr_image(image)`**: Sends an image to Google Cloud Vision API for OCR and returns the extracted text.
- **`post_process_text(text)`**: Cleans up the extracted text.
- **`combine_images(images, pages_per_image)`**: Combines multiple images into a single image.
- **`process_pdf(pdf_path, pages_per_image)`**: Converts PDF pages to images, performs OCR, and returns the extracted text.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
