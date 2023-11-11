# gpt_pdf_md

gpt_pdf_md is a Python package which uses GPT-4V and other tools to convert pdf into Markdown files. current limitation of raw gpt-4v is that that it does not support pdf documents in the api and if prompted to convert text which contains figures to markdown, figures are not getting not converted correctly because the image url in the markdown is missing. IT TURNS OUT gpt_pdf_md IS EVEN COMING CLOSE TO OCR QUALITY OF MATHPIX!

## Features

- Extracts figures from PDF files using the `pdffigures2` Scala library.
- Converts PDF pages to images and uploads them to Google Cloud Bucket.
- Utilizes GPT-4V Vision to generate Markdown content from pdf an than inserts image urls into markdown.

## Additional Dependencies

This package requires the `pdffigures2` Scala library to extract figures from PDF files. You need to have all necessary dependencies installed for the library https://github.com/allenai/pdffigures2. (this can be quite a hassle because parts of the library are written in scala so you need to have the right version of java and scala installed - we are looking for an alternative, more easy going way to extract images from a pdf, if youn have any ideas, feel free open an [issue](https://github.com/yachty66/gpt_vision_plus/issues) on that)

## Installation

Once you have `pdffigures2` setup you can install gpt_pdf_md via pip:

```bash
pip install gpt-pdf-md
```

Configure the required environment variables in your .env file without spaces or unnecessary quotes:

```env
OPENAI_API_KEY=open_ai_key
GOOGLE_ID=google_project_id
GOOGLE_BUCKET=google_bucket_name
```

NOTE: the project requires a public google bucket where the images which later are getting rendered in the markdown are getting uploaded to.

## Usage

To process a PDF and generate Markdown content its important that the python file is in the same directory than the `pdffigures2` folder. You can use the gpt_pdf_md as following:

```python
from gpt_pdf_md.reader import process_pdf
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
```

This will process the specified PDF and output a Markdown file with the extracted information in the same directory. An example is the `output.md` file which is the converted result of `example.pdf`

## Next steps

- [ ] try rust [vortex](https://github.com/omkar-mohanty/vortex) for pdf image extraction
- [ ] use gpt-4 128k for final formatting of markdown
- [ ] clearer readme to make it easier for everyone to use the python package
- [ ] error handling  

## Contributing & Support

We welcome contributions! Please open an issue or submit a pull request on our GitHub repository.

## License

This project is licensed under the terms of the [MIT License](gpt_pdf_md/LICENSE).


