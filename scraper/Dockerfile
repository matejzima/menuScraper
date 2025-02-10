FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your Python scripts
COPY . /app/

# By default, do nothing. We'll run the scripts on demand or via schedule.
CMD ["python", "update_index.py"]