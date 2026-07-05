FROM python:3.8-slim-buster

RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list && \
    apt update
RUN apt install -y python3-opencv wget

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN sed -i "s/F.hardswish(input, self.inplace)/F.hardswish(input)/" /usr/local/lib/python3.8/site-packages/torch/nn/modules/activation.py
COPY . .
RUN ["/bin/bash"]