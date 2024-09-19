import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from google.cloud import vision
from google.cloud.vision_v1 import types
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import re
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import google.generativeai as genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up Google Cloud Vision client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/ocr_gcp_api_key.json'
vision_client = vision.ImageAnnotatorClient()

# Register a Unicode font that supports Vietnamese characters
font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
addMapping('DejaVuSans', 0, 0, 'DejaVuSans')

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ocr_image(image):
  # Perform OCR using Google Cloud Vision API
  image = types.Image(content=image)
  response = vision_client.document_text_detection(image=image)
  return response.full_text_annotation.text

def post_process_text(text):
  # Remove excessive newlines
  text = re.sub(r'\n{3,}', '\n\n', text)
  # Remove lines with only spaces
  text = '\n'.join([line for line in text.split('\n') if line.strip()])
  
  # Example API call to enhance text
  #enhanced_text = enhance_text_with_LLM(text)
  #text = enhanced_text
  return text

def enhance_text_with_LLM(text):
    # Step 1: Read the API key from the file
    with open('secrets/gemini_api_key.txt', 'r') as file:
      GEMINI_API_KEY = file.read().strip()

    # Initialize the generative model
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Construct the input prompt with pre-instruction
    prompt = (
        "You are an expert in text correction. I have a text output from an OCR system containing Vietnamese language content. "
        "The OCR output may have errors. Please provide the corrected version of the text without any explanations or additional comments.\n\n"
        "Here is the OCR output that needs enhancement:\n\n"
        f"{text}"
    )
    
    # Generate the enhanced text
    response = model.generate_content(prompt)
    
    return response.text

def combine_images(images, pages_per_image=1):
  combined_images = []
  for i in range(0, len(images), pages_per_image):
      batch = images[i:i+pages_per_image]
      widths, heights = zip(*(i.size for i in batch))
      max_width = max(widths)
      total_height = sum(heights)
      combined_image = Image.new('RGB', (max_width, total_height))
      y_offset = 0
      for img in batch:
          combined_image.paste(img, (0, y_offset))
          y_offset += img.size[1]
      combined_images.append(combined_image)
  return combined_images

def process_pdf(pdf_path, pages_per_image=2):
  poppler_path = r'D:\ProgramFiles\poppler\Library\bin'  # Update this path to your Poppler installation
  images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=300)
  combined_images = combine_images(images, pages_per_image)
  text = ""
  for image in combined_images:
      # Convert PIL Image to bytes
      img_byte_arr = io.BytesIO()
      image.save(img_byte_arr, format='PNG')
      img_byte_arr = img_byte_arr.getvalue()
      
      text += ocr_image(img_byte_arr) + "\n\n"
      #print(text)
  return post_process_text(text)

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
          pages_per_image = int(request.form.get('pages_per_image', 2))
          text = process_pdf(filepath, pages_per_image)
          
          # Create a new PDF with the extracted text
          output = io.BytesIO()
          c = canvas.Canvas(output, pagesize=letter)
          width, height = letter
          font_name = "DejaVuSans"
          font_size = 10
          
          def add_text_to_page(text_lines):
              c.setFont(font_name, font_size)
              y = height - 40
              for line in text_lines:
                  if y < 40:
                      c.showPage()
                      c.setFont(font_name, font_size)  # Reset font for new page
                      y = height - 40
                  c.drawString(40, y, line.encode('utf-8').decode('utf-8'))
                  y -= 14
          
          # Split text into pages
          lines = text.split('\n')
          lines_per_page = int((height - 80) // 14)  # Ensure lines_per_page is an integer
          
          for i in range(0, len(lines), lines_per_page):
              page_lines = lines[i:i+lines_per_page]
              add_text_to_page(page_lines)
              if i + lines_per_page < len(lines):
                  c.showPage()  # Start a new page if there's more text
          
          c.save()
          output.seek(0)
          
          # Clean up the uploaded file
          os.remove(filepath)
          
          # Create the download name with the original file name prefixed by "ocr_"
          original_name = os.path.splitext(filename)[0]  # Get the original file name without extension
          download_name = f"ocr_{original_name}.pdf"
          
          return send_file(output, as_attachment=True, download_name=download_name, mimetype='application/pdf')
  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)