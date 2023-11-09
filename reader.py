from PyPDF2 import PdfReader
import json
import shutil
from google.cloud import storage
import requests
from pdf2image import convert_from_path
import re
import base64
import io
import os
import subprocess
from dotenv import load_dotenv
import tempfile

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_ID = os.getenv('GOOGLE_ID')
GOOGLE_BUCKET = os.getenv('GOOGLE_BUCKET')

CURRENT_DIR = os.getcwd()
PDF_DIR = CURRENT_DIR + "/pdffigures2/pdf_dir/"
PDF_FILE = CURRENT_DIR + "/pdffigures2/pdf_dir/main.pdf"
PDFFIGURES2_PATH = CURRENT_DIR + "/pdffigures2/"

def main(pdf):
    """
    control flow of app
    """
    shutil.copy(pdf, PDF_FILE)
    extract_figures(PDFFIGURES2_PATH, PDF_DIR)
    base64_images = pdf_to_image(PDF_FILE)
    for i, base64_image in enumerate(base64_images):
        markdown(base64_image, i)

def number_pages_pdf(pdf_file):
    """
    get the number of pages of the pdf
    """
    with open(pdf_file, "rb") as file:
        pdf = PdfReader(file)
        number_of_pages = len(pdf.pages)
    return number_of_pages

def extract_figures(library_path, pdf_path):
    """
    executes pdffigures2 for extracting figures from pdf. expects pdf from which images should be extracted to be at pdffigures2/pdf_dir/ and saves all extracted images also in this directory
    """
    original_dir = os.getcwd()
    os.chdir(library_path)
    command = [
        "sbt",
        f'"runMain org.allenai.pdffigures2.FigureExtractorBatchCli {pdf_path} -d {pdf_path} -m {pdf_path}"'
    ]
    subprocess.run(" ".join(command), shell=True, check=True)
    os.chdir(original_dir)

def convert_pdf_to_images(pdf_path):
    """
    Convert each page of the PDF to an image
    """
    return convert_from_path(pdf_path)

def convert_image_to_base64(image):
    """
    Convert an image to a base64 string
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')

def pdf_to_image(pdf_file):
    """
    Convert each page of the PDF to a base64 string
    """
    images = convert_pdf_to_images(pdf_file)
    return [convert_image_to_base64(image) for image in images]

def title():
    """
    gets the title of the pdf which is processed
    """
    pass

def markfown_file_tail():
    """
    gets last three sentences of output.md. if no output.md exists creates new one
    """
    if not os.path.exists('output.md'):
        with open('output.md', 'w') as f:
            f.write('')
    with open('output.md', 'r') as f:
        content = f.read()
    sentences = content.split('.')
    last_three_sentences = '.'.join(sentences[-3:])
    return last_three_sentences

def markdown(base64_image, page):
    """
    iterates over all images, converts them to markdown and adds them up to one markdown file
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    markdown_tail = markfown_file_tail()
    prompt = f"""
    Please provide the content of the paper in Markdown format. The Markdown file where you write your content in has the following content (last three sentences are getting displayed and none if empty):

    {markdown_tail}

    For math, use LaTeX format; that is, enclose inline equations within a pair of dollar signs, and use double dollar signs for block (display) equations. In the case you are seeing a figure please mark this approriate. Do not include tick marks (```markdown```) and only respond with the Markdown and no additional elaboration.
    """

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()
    content = response_json['choices'][0]['message']['content']
    response_images_inserted = insert_images(content, page)
    with open('output.md', 'a') as f:
        f.write(response_images_inserted)

def insert_images(markdown, page):
    """
    Replace all figure links in the markdown with the given image URL
    """
    # Define the pattern for figure links
    pattern = r'\(attachment:image.png\)'
    image_paths = get_image_paths(page)
    image_urls = upload_images(image_paths)
    # Replace each occurrence of the pattern with the corresponding image URL
    for image_url in image_urls:
        markdown = re.sub(pattern, f'({image_url})', markdown, count=1)
    return markdown

def get_image_paths(page):
    """
    Gets the paths to all the images from the current page
    """
    # Load the JSON data
    path = PDF_DIR + 'main.json'
    with open(path) as f:
        data = json.load(f)
    # Filter the figures for the current page and extract the image paths
    image_paths = [figure['renderURL'] for figure in data if figure['page'] == page]
    return image_paths

def upload_images(image_paths):
    """
    Uploads all images from the current page to the Google Cloud Storage bucket and returns their URLs
    """
    # Initialize the Google Cloud Storage client
    client = storage.Client(project=GOOGLE_ID)
    # Get the bucket
    bucket = client.get_bucket(GOOGLE_BUCKET)
    image_urls = []
    for image_path in image_paths:
        # Define the blob (name) for the image in the bucket
        blob = bucket.blob(os.path.basename(image_path))
        # Upload the image to the bucket
        blob.upload_from_filename(image_path)
        # Get the URL of the uploaded image
        image_url = blob.public_url
        image_urls.append(image_url)
    return image_urls

if __name__ == "__main__":
    main()