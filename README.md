full steps and code for creating a Flask application that performs OCR on PDF files using Tesseract, targeting the Vietnamese language, on Windows 11. I'll include the installation steps for Tesseract as well.

Step 1: Install Tesseract OCR

Download Tesseract OCR for Windows:
Go to https://github.com/UB-Mannheim/tesseract/wiki
Download the latest 64-bit version (e.g., tesseract-ocr-w64-setup-v5.3.1.20230401.exe)
Run the installer:
Choose the installation directory (e.g., C:\Program Files\Tesseract-OCR)
Select "Additional language data (download)" during installation
In the additional language data, select "Vietnamese"
Add Tesseract to System PATH:
Right-click on the Start button and select "System"
Click on "Advanced system settings"
Click on "Environment Variables"
Under "System variables", find and select the "Path" variable, then click "Edit"
Click "New" and add the path to the Tesseract installation directory (e.g., C:\Program Files\Tesseract-OCR)
Click "OK" to close all dialogs
Step 2: Install Python and required libraries

Download and install Python from https://www.python.org/downloads/ (if not already installed)
Open a command prompt and run:
   pip install flask pytesseract pdf2image PyPDF2 Pillow
Step 3: Install Poppler (required for pdf2image)

Download Poppler for Windows from https://github.com/oschwartz10612/poppler-windows/releases/
Extract the contents to a folder (e.g., C:\poppler)
Add the Poppler bin directory to your system PATH (similar to step 1.3)
Step 4: Create the Flask application

Create a new directory for your project
Inside the project directory, create a new file named app.py
Create a folder named templates in the project directory
Inside the templates folder, create a file named index.html
Step 5: Implement the Flask application