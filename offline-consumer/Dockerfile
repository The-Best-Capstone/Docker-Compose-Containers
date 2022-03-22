FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt
ADD offline-consumer.py .

CMD ["python3", "-u", "./offline-consumer.py"]
