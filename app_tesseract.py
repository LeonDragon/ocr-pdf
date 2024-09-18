import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'D:\ProgramFiles\Tesseract-OCR\tesseract.exe'

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ocr_image(image):
  return pytesseract.image_to_string(image, lang='vie')

def process_pdf(pdf_path):
  poppler_path = r'D:\ProgramFiles\poppler\Library\bin'  # Update this path to your Poppler installation
  images = convert_from_path(pdf_path, poppler_path=poppler_path)
  text = ""
  for image in images:
      text += ocr_image(image) + "\n\n"
      print(text)
  return text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
      if 'file' not in request.files:
          return render_template('index.html', error='No file part')
      file = request.files['file']
      if file.filename == '':
          return render_template('index.html', error='No selected file')
      if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          file.save(filepath)
          
          # Process the PDF
          text = process_pdf(filepath)
          
          # Create a new PDF with the extracted text
          output = io.BytesIO()
          c = canvas.Canvas(output, pagesize=letter)
          width, height = letter
          c.setFont("Helvetica", 10)
          y = height - 40
          for line in text.split('\n'):
              if y < 40:
                  c.showPage()
                  y = height - 40
              c.drawString(40, y, line)
              y -= 14
          c.save()
          output.seek(0)
          
          # Clean up the uploaded file
          os.remove(filepath)
          
          return send_file(output, as_attachment=True, download_name='ocr_result.pdf', mimetype='application/pdf')
  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)