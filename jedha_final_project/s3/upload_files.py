import os
import boto3
import dotenv
import pandas as pd

# from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv("./.env"))

# BUCKET_NAME = "tgiandoriggio-bucket-kayak-01"

# root = "csv_files"
# filenames = ["weather_data.csv",
#              "hotel_data.csv"]

# session = boto3.Session(aws_access_key_id=os.getenv("AWS_KEY"),
#                         aws_secret_access_key=os.getenv("AWS_SECRET"))

# s3 = session.resource("s3")
# bucket = s3.create_bucket(Bucket=BUCKET_NAME)

# for file in filenames:
#     path = f"{root}/{file}"
#     if not os.path.isfile(path):
#         raise FileExistsError(f"{path} does not exist.")

#     data = pd.read_csv(path)
#     csv = data.to_csv(index=False)
#     put_object = bucket.put_object(Key=file, Body=csv)

if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv("./.env"))