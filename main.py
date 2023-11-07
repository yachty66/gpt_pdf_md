"""
q is also a bit how to get this all working together

do i want to feed paper in or do i want to feed in a single image to feed into it. i think i want to feed single image. let the current imgur be the example
"""

#import openai


"""
Please provide the content of the paper into markdown format. For math use latex format, i.e. within a pair of dollar signs for inline equations, and double dollar signs for block (display) equations.

"""
import fitz

def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            base = pdf_path.split('/')[-1]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix.save("images/%s.png" % (base + "_"+ str(i)), "png")
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save("images/%s.png" % (base + "_"+ str(i)), "png")
                pix1 = None
            pix = None

extract_images_from_pdf('example.pdf')




"""messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please provide the content of the paper into markdown format. For math use latex format, i.e. within a pair of dollar signs for inline equations, and double dollar signs for block (display) equations."},
                {
                    "type": "image_url",
                    "image_url": "https://i.imgur.com/6UKumeu.png",
                },
            ],
        }
    ]

response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=2000
)
result = response.choices[0]
with open('output.md', 'w') as f:
    f.write(result['message']['content'])
print(result)


def reader(image_url, path, return_file, bucket):
    # Your code here
    pass"""

