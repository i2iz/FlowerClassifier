FROM python:3.11

WORKDIR /app

COPY . /app/

# 한글 깨짐 방지
RUN apt-get update && apt-get install -y \
    fonts-nanum \
    && fc-cache -fv

RUN pip install --no-cache-dir tensorflow==2.17.0 numpy==1.26.4 pandas==2.2.2 pillow==10.4.0 openpyxl==3.1.5