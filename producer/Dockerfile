FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD producer.py .
ADD config.json .

CMD ["python3", "-u", "./producer.py"]
