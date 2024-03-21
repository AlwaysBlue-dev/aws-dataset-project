# get_s3_urls.py
import os
import django
import boto3
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DataSetWeb.settings')
django.setup()

from main_app.models import Product

def get_s3_object_urls(bucket_name, folder_name):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, 
                      region_name=settings.AWS_S3_REGION_NAME,
                      config=boto3.session.Config(signature_version='s3v4'))
                      
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

    urls = []
    for page in pages:
        for obj in page.get('Contents', []):
            object_key = obj['Key']
            # Check if the object is a file (not the folder itself or another subfolder)
            if not object_key.endswith('/') and object_key != folder_name:
                url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
                urls.append(url)

    return urls



def save_urls_to_database(urls):
    for url in urls:
        # Check if the URL already exists in the database
        existing_product = Product.objects.filter(file_path=url).first()
        
        if existing_product:
            # Update the existing entry
            existing_product.save()
        else:
            # Create a new entry
            product_obj = Product(file_path=url)
            product_obj.save()


