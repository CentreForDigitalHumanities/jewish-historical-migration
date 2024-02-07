# Base image
FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update
RUN apt-get -y install gdal-bin

# make a directory in the container
WORKDIR /backend
# copy files from the host system to the directory in the container
COPY requirements.txt /backend/
# run pip install on container
RUN pip install -r requirements.txt
