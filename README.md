# gpt_pdf_md

`gpt_pdf_md` is a Python package that leverages GPT-4V and other tools to convert PDF files into Markdown. The current limitation of raw GPT-4V is that it does not support PDF documents in the API. Additionally, when prompted to convert text containing figures to Markdown, the figures are not converted correctly due to missing image URLs in the Markdown. However, `gpt_pdf_md` is coming close to the OCR quality of Mathpix!

## Features

- Extracts figures from PDF files using the `pdffigures2` Scala library.
- Converts PDF pages to images and uploads them to a Google Cloud Bucket.
- Utilizes GPT-4V Vision to generate Markdown content from a PDF and then inserts image URLs into the Markdown.

## Additional Dependencies

This package requires the `pdffigures2` Scala library to extract figures from PDF files. You need to have all necessary dependencies installed for the library. You can find more information [here](https://github.com/allenai/pdffigures2). Please note that this can be quite a hassle because parts of the library are written in Scala, so you need to have the correct versions of Java and Scala installed. We are looking for an alternative, more straightforward way to extract images from a PDF. If you have any ideas, feel free to open an [issue](https://github.com/yachty66/gpt_pdf_md/issues).

## Installation

Once you have `pdffigures2` set up, you can install `gpt_pdf_md` via pip:

```bash
pip install gpt-pdf-md
```

Configure the required environment variables in your `.env` file without spaces or unnecessary quotes:

```env
OPENAI_API_KEY=open_ai_key
GOOGLE_ID=google_project_id
GOOGLE_BUCKET=google_bucket_name
```

NOTE: This project requires a public Google bucket where the images, which are later rendered in the Markdown, are uploaded.

## Usage

To process a PDF and generate Markdown content, it's important that the Python file is in the same directory as the `pdffigures2` folder. You can use `gpt_pdf_md` as follows:

```python
from gpt_pdf_md.reader import process_pdf
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_ID = os.getenv('GOOGLE_ID')
GOOGLE_BUCKET = os.getenv('GOOGLE_BUCKET')

absolute_path = os.path.dirname(os.path.abspath(__file__))
# Absolute path to the PDF file
PDF = absolute_path + "/example.pdf"
# Absolute path to pdffigures2
PDFFIGURES2_PATH = absolute_path + "/pdffigures2/"
process_pdf(PDF, PDFFIGURES2_PATH, OPENAI_API_KEY, GOOGLE_ID, GOOGLE_BUCKET)
```

This will process the specified PDF and output a Markdown file with the extracted information in the same directory. An example is the `output.md` file, which is the converted result of `example.pdf` created by running the `example.py` script.

## Next Steps

- [ ] Try Rust [vortex](https://github.com/omkar-mohanty/vortex) for PDF image extraction
- [ ] Use GPT-4 128k for final formatting of Markdown
- [ ] Create a clearer README to make it easier for everyone to use the Python package
- [ ] Improve error handling

## Contributing & Support

We welcome contributions! Please open an issue or submit a pull request on our GitHub repository.

## License

This project is licensed under the terms of the [MIT License](gpt_pdf_md/LICENSE).