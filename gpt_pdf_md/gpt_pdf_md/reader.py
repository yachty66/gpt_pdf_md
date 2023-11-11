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
import glob
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_pdf(pdf, pdffigures2_path, openai_api_key, google_id, google_bucket):
    """Controls the main flow of the application."""
    logging.info("Starting process_pdf function")
    OPENAI_API_KEY = openai_api_key
    GOOGLE_ID = google_id
    GOOGLE_BUCKET = google_bucket
    PDF_DIR = os.path.join(pdffigures2_path, "pdf_dir/")
    PDF_FILE = os.path.join(PDF_DIR, "main.pdf")
    shutil.copy(pdf, PDF_FILE)
    extract_figures(pdffigures2_path, PDF_DIR)
    base64_images = pdf_to_image(PDF_FILE)
    for i, base64_image in enumerate(base64_images):
        markdown(base64_image, i, OPENAI_API_KEY, GOOGLE_ID, GOOGLE_BUCKET, PDF_DIR)
    clear_directory(PDF_DIR)
    logging.info("Finished process_pdf function")


def clear_directory(pdf_path):
    """Removes all files in the specified directory."""
    logging.info(f"Clearing directory: {pdf_path}")
    files = glob.glob(pdf_path + "*")
    for f in files:
        os.remove(f)
    logging.info(f"Finished clearing directory: {pdf_path}")


def number_pages_pdf(pdf_file):
    """Gets the number of pages from the pdf"""
    logging.info(f"Getting number of pages for PDF: {pdf_file}")
    with open(pdf_file, "rb") as file:
        pdf = PdfReader(file)
        number_of_pages = len(pdf.pages)
    logging.info(f"Number of pages in PDF: {number_of_pages}")
    return number_of_pages


def extract_figures(library_path, pdf_path):
    """Extracts figures from the PDF using the pdffigures2 library."""
    logging.info("Starting extract_figures function")
    original_dir = os.getcwd()
    os.chdir(library_path)
    command = [
        "sbt",
        f'"runMain org.allenai.pdffigures2.FigureExtractorBatchCli {pdf_path} -d {pdf_path} -m {pdf_path}"',
    ]
    subprocess.run(" ".join(command), shell=True, check=True)
    os.chdir(original_dir)
    logging.info("Finished extract_figures function")


def convert_pdf_to_images(pdf_path):
    """Converts each page of the PDF to an image."""
    return convert_from_path(pdf_path)


def convert_image_to_base64(image):
    """Converts an image to a base64 string."""
    logging.info("Starting convert_image_to_base64 function")
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    logging.info("Finished convert_image_to_base64 function")
    return img_str.decode("utf-8")


def pdf_to_image(pdf_file):
    """Converts each page of the PDF to a base64 string."""
    logging.info("Starting pdf_to_image function")
    images = convert_pdf_to_images(pdf_file)
    logging.info("Finished pdf_to_image function")
    return [convert_image_to_base64(image) for image in images]


def markfown_file_tail():
    """Returns the last three sentences of 'output.md' or creates the file if it doesn't exist."""
    logging.info("Starting markfown_file_tail function")
    if not os.path.exists("output.md"):
        with open("output.md", "w") as f:
            f.write("")
    with open("output.md", "r") as f:
        content = f.read()
    sentences = content.split(".")
    last_three_sentences = ".".join(sentences[-3:])
    logging.info("Finished markfown_file_tail function")
    return last_three_sentences


def markdown(base64_image, page, openai_api_key, google_id, google_bucket, pdf_dir):
    """Converts images to markdown and appends them to a markdown file."""
    logging.info("Starting markdown function")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
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
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.0,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response_json = response.json()
    content = response_json["choices"][0]["message"]["content"]
    response_images_inserted = insert_images(
        content, page, google_id, google_bucket, pdf_dir
    )
    with open("output.md", "a") as f:
        f.write(response_images_inserted)
    logging.info("Finished markdown function")


def insert_images(markdown, page, google_id, google_bucket, pdf_dir):
    """Replaces figure links in the markdown with the corresponding image URL."""
    logging.info("Starting insert_images function")
    # Define the pattern for figure links
    pattern = r"\(attachment:image.png\)"
    image_paths = get_image_paths(page, pdf_dir)
    image_urls = upload_images(image_paths, google_id, google_bucket)
    # Replace each occurrence of the pattern with the corresponding image URL
    for image_url in image_urls:
        markdown = re.sub(pattern, f"({image_url})", markdown, count=1)
    logging.info("Finished insert_images function")
    return markdown


def get_image_paths(page, pdf_dir):
    """Returns the paths to all images from the current page."""
    logging.info("Starting get_image_paths function")
    # Load the JSON data
    path = pdf_dir + "main.json"
    with open(path) as f:
        data = json.load(f)
    # Filter the figures for the current page and extract the image paths
    image_paths = [figure["renderURL"] for figure in data if figure["page"] == page]
    logging.info("Finished get_image_paths function")
    return image_paths


def upload_images(image_paths, google_id, google_bucket):
    """Uploads images to Google Cloud Storage and returns their URLs."""
    logging.info("Starting upload_images function")
    # Initialize the Google Cloud Storage client
    client = storage.Client(project=google_id)
    # Get the bucket
    bucket = client.get_bucket(google_bucket)
    image_urls = []
    for image_path in image_paths:
        # Define the blob (name) for the image in the bucket
        blob = bucket.blob(os.path.basename(image_path))
        # Upload the image to the bucket
        blob.upload_from_filename(image_path)
        # Get the URL of the uploaded image
        image_url = blob.public_url
        image_urls.append(image_url)
    logging.info("Finished upload_images function")
    return image_urls
