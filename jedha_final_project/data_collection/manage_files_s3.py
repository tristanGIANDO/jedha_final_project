import os
import boto3
import pandas as pd
from dotenv import load_dotenv, find_dotenv

import envs

load_dotenv(find_dotenv("./.env"))

BUCKET_NAME = envs.BUCKET_NAME

session = boto3.Session(aws_access_key_id=os.getenv("AWS_KEY"),
                        aws_secret_access_key=os.getenv("AWS_SECRET"))

s3 = session.resource("s3")


def post_files(files: list[str]) -> None:
    global session
    global s3

    objects = []

    bucket = s3.create_bucket(Bucket=BUCKET_NAME)

    for file in files:
        if not os.path.isfile(file):
            raise FileExistsError(f"{file} does not exist.")

        data = pd.read_csv(file)
        csv = data.to_csv(index=False)
        put_object = bucket.put_object(Key=os.path.basename(file), Body=csv)
        objects.append(put_object)

    return objects


def get_files(files: list[str]) -> list[str]:
    global session
    global s3

    bucket = s3.Bucket(BUCKET_NAME)

    # Access to temp
    temp_dir = os.path.join("AppData", "Local", "Temp")
    os.makedirs(temp_dir, exist_ok=True)

    # download file
    downloaded_files = []
    for obj in bucket.objects.all():
        file_key = obj.key
        if file_key in files:
            file_path = os.path.join(temp_dir, file_key)
            bucket.download_file(file_key, file_path)
            downloaded_files.append(file_path)

    return downloaded_files


if __name__ == "__main__":
    # send files
    objects = post_files(["jedha_final_project/data_collection/test_file.csv"])
    print(objects)

    # download files
    file_list = ["test_file.csv"]
    downloaded_files = get_files(file_list)

    if downloaded_files:
        df = pd.read_csv(downloaded_files[0])
        print(df.head())
