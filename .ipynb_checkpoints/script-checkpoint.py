import boto3
import os
import sys
from botocore.exceptions import BotoCoreError, ClientError

## Image Source: 
# https://www.twine.net/blog/facial-recognition-datasets/
# https://drive.google.com/drive/folders/1tZUcXDBeOibC6jcMCtgRRz67pzrAHeHL

def create_collection(collection_id):
    """Create a Rekognition collection if it does not exist."""
    rekognition_client = boto3.client("rekognition")
    try:
        rekognition_client.create_collection(CollectionId=collection_id)
        print(f"Collection {collection_id} created successfully.")
    except rekognition_client.exceptions.ResourceAlreadyExistsException:
        print(f"Collection {collection_id} already exists.")
    except (BotoCoreError, ClientError) as e:
        print(f"Error creating collection {collection_id}: {e}")

def list_images_in_s3(bucket_name, prefix):
    """List all images in the given S3 bucket and prefix."""
    s3_client = boto3.client("s3")
    image_list = []
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                if obj["Key"].lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_list.append(obj["Key"])
    except ClientError as e:
        print(f"Error listing objects in S3: {e}")
    return image_list

def index_faces(collection_id, bucket_name, image_key):
    """Index an image in Amazon Rekognition Collection."""
    rekognition_client = boto3.client("rekognition")
    try:
        response = rekognition_client.index_faces(
            CollectionId=collection_id,
            Image={"S3Object": {"Bucket": bucket_name, "Name": image_key}},
            ExternalImageId=image_key.split("/")[-1],
            DetectionAttributes=["DEFAULT"],
            MaxFaces=1,
            QualityFilter="AUTO"
        )
        if response['FaceRecords']:
            print(f"Indexed {image_key}")
        else:
            print(f"No face detected in {image_key}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error indexing image {image_key}: {e}")

def process_s3_images(bucket_name, parent_prefix, collection_id):
    """Iterate through S3 images and index them in Rekognition."""
    create_collection(collection_id)
    images = list_images_in_s3(bucket_name, parent_prefix)
    print(f"Found {len(images)} images. Indexing...")
    for image_key in images:
        index_faces(collection_id, bucket_name, image_key)
    print("Indexing complete!")

def search_face(collection_id, local_image_path, bucket_name, s3_image_key):
    """Search for a given face in the Rekognition collection."""
    rekognition_client = boto3.client("rekognition")
    s3_client = boto3.client("s3")
    
    try:
        # Upload image to S3
        s3_client.upload_file(local_image_path, bucket_name, s3_image_key)
        print(f"Uploaded {local_image_path} to s3://{bucket_name}/{s3_image_key}")
        
        # Search for the face in Rekognition
        response = rekognition_client.search_faces_by_image(
            CollectionId=collection_id,
            Image={"S3Object": {"Bucket": bucket_name, "Name": s3_image_key}},
            MaxFaces=1,
            FaceMatchThreshold=90
        )
        
        matches = response.get("FaceMatches", [])
        if matches:
            print(f"Face found! Similarity: {matches[0]['Similarity']}%")
        else:
            print("No match found.")
        return matches
    except (BotoCoreError, ClientError) as e:
        print(f"Error searching for face: {e}")
        return []

if __name__ == "__main__":
    action = sys.argv[1]  # 'index' or 'search'
    collection_id = "FacesCollection"
    bucket_name = "your-s3-bucket-name"
    
    if action == "index":
        parent_prefix = "users/"  # Adjust this based on your structure
        process_s3_images(bucket_name, parent_prefix, collection_id)
    elif action == "search":
        local_image_path = sys.argv[2]
        s3_image_key = f"temp/{os.path.basename(local_image_path)}"
        search_face(collection_id, local_image_path, bucket_name, s3_image_key)
    else:
        print("Usage: python script.py [index|search] [local_image_path if search]")
