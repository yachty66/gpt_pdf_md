"""
i need to get this scala stuff working otherwise i am going to extract incorrect.



"""

from PyPDF2 import PdfReader

reader = PdfReader("cats.pdf")

page = reader.pages[0]
count = 0

for image_file_object in page.images:
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
        count += 1
#sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli /Users/maxhager/projects_2023/gpt_vision_plus/pdffigures2/pdf_dir/"

#/Users/maxhager/projects_2023/gpt_vision_plus/pdffigures2/pdf_dir/

#sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli /Users/maxhager/projects_2023/gpt_vision_plus/pdffigures2/pdf_dir/ -d /Users/maxhager/projects_2023/gpt_vision_plus/pdffigures2/pdf_dir/ -m /Users/maxhager/projects_2023/gpt_vision_plus/pdffigures2/pdf_dir/"


#sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli /path/to/pdf_directory/ -d /path/to/figure/data/ -m /path/to/figure/images/"