FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir rpi.gpio

ADD max31855.py .

CMD ["python3", "-u", "./max31855.py"]
