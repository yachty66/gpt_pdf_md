from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name='gpt_pdf_md',
    version='0.2',
    packages=find_packages(),
    description='A Python package that utilizes GPT-4V and other tools to convert PDFs into Markdown files.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Max Hager',
    author_email='maxhager28@gmail.com',
    install_requires=required_packages,
)