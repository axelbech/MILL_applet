FROM python:3.8-slim-buster

COPY met_test.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "./mill.py"]