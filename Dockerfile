FROM python:3.6-slim
MAINTAINER Tiffany Ensor "tiffany_ensor@hotmail.com"

RUN apt-get update \
    && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgtk2.0-dev

RUN mkdir /opt/knitting_app/
WORKDIR /opt/knitting_app/

# install requirements
ADD ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# startup command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]