FROM python:3.9-alpine
ARG CACHEBUST=1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "update_index.py"]
