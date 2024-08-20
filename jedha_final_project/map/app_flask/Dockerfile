FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update
RUN apt-get install -y nano unzip curl

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD ["python", "app.py"]
