from google.cloud import storage

client = storage.Client()

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
