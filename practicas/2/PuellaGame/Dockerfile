FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY default_store/ /default_store/
ENV STORE_DIR=/store \
    DEFAULT_STORE_DIR=/default_store
RUN mkdir -p /store

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
