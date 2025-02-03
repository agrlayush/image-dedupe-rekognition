# Image Deduplication with Amazon Rekognition

This project provides a Python-based image deduplication system using AWS Rekognition. It indexes user images stored in an S3 bucket and allows searching for duplicate images to detect if a user has already applied.

## Features
- Indexes faces from images stored in an S3 bucket.
- Searches for duplicate faces using Rekognition's `search_faces_by_image` API.
- Automatically creates a Rekognition collection if it does not exist.

## Prerequisites
- AWS Account with necessary IAM permissions for Rekognition and S3.
- Python 3.x installed with `boto3`.
- An S3 bucket containing user images.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/agrlayush/image-dedupe-rekognition.git
   cd image-dedupe-rekognition
   ```
2. Install dependencies:
   ```sh
   pip install boto3
   ```

## Usage

### 1. Index Images in S3
Run the following command to index all images in the S3 bucket:
```sh
python script.py index
```
This will scan images under the `users/` directory in S3 and index them in Rekognition.

### 2. Search for a Face
To check if a face already exists, run:
```sh
python script.py search /path/to/local/image.jpg
```
This will upload the image temporarily to S3 and search for matches in Rekognition.

## Configuration
Modify `script.py` to set:
- `collection_id`: Name of the Rekognition collection.
- `bucket_name`: Your S3 bucket name.
- `parent_prefix`: The folder path in S3 where user images are stored.

## Notebook
You can use the `rekognition-dedupe.ipynb` notebook file to test the implementation on Jupyter Notebook

