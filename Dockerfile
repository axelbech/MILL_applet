FROM python:3.8-slim-buster

WORKDIR /

COPY . .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "./mill.py"]