from google.cloud import storage
import os

def upload_images():
    """
    Uploads all images from the current page to the Google Cloud Storage bucket and returns their URLs
    """
    # Initialize the Google Cloud Storage client
    client = storage.Client(project='mbtichat-388909')

    # Get the bucket
    bucket = client.get_bucket('mathreader')

    image_urls = []

    # Define the blob (name) for the image in the bucket
    blob = bucket.blob(os.path.basename("main-Table4-1.png"))

    # Upload the image to the bucket
    blob.upload_from_filename("main-Table4-1.png")

    # Get the URL of the uploaded image
    image_url = blob.public_url
    image_urls.append(image_url)
    print(image_urls)

    return image_urls

upload_images()