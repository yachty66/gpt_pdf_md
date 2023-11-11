from gptpdfreader.reader import process_pdf
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_ID = os.getenv('GOOGLE_ID')
GOOGLE_BUCKET = os.getenv('GOOGLE_BUCKET')

absolute_path = os.path.dirname(os.path.abspath(__file__))
#absolute path to pdf file
PDF = absolute_path + "/example.pdf"
#absolute padth to pdffigures2
PDFFIGURES2_PATH = absolute_path + "/pdffigures2/"
process_pdf(PDF, PDFFIGURES2_PATH, OPENAI_API_KEY, GOOGLE_ID, GOOGLE_BUCKET)
