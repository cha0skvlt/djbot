FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .env

RUN python - <<'PY'
import database
database.init_databases()
PY

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
