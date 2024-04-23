FROM python:3.11
WORKDIR /app
COPY . /app
RUN apt-get -qq update && apt-get -qq install -y git wget ffmpeg mediainfo
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
