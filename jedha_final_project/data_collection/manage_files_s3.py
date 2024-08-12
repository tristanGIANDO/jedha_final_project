import os
import boto3
import pandas as pd
from dotenv import load_dotenv, find_dotenv

import envs

load_dotenv(find_dotenv("./.env"))

BUCKET_NAME = envs.BUCKET_NAME


def post_files(files: list[str]) -> None:
    """Post CSV files to S3 bucket

    Args:
        files (list[str]): local path of the files

    Raises:
        FileExistsError: file does not exist

    Returns:
        _type_: created bucket
    """
    session = boto3.Session(aws_access_key_id=os.getenv("AWS_KEY"),
                            aws_secret_access_key=os.getenv("AWS_SECRET"))

    s3 = session.resource("s3")

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
    """Download files. To use only if connection issues

    Args:
        files (list[str]): path of file on S3

    Returns:
        list[str]: downloaded files
    """
    session = boto3.Session(aws_access_key_id=os.getenv("AWS_KEY"),
                            aws_secret_access_key=os.getenv("AWS_SECRET"))

    s3 = session.resource("s3")

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
    # send CSV
    objects = post_files(["jedha_final_project/data_collection/test_file.csv"])
    print(objects)

    # # read CSV
    # df = pd.read_csv("https://jedha-final-project-jrat.s3.amazonaws.com/dictionnaire_donnees_parc.csv")
    # print(df.head())
