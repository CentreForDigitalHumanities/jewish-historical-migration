# Base image
FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update
RUN apt-get -y install gdal-bin
RUN pip install pip-tools

# make a directory in the container
WORKDIR /backend
# copy files from the host system to the directory in the container
COPY requirements.in /backend/
RUN pip-compile
# run pip install on container
RUN pip install -r requirements.txt
