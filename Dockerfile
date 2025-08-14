FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y make python3.12-venv && make env

EXPOSE 8000

CMD ["conda", "run", "-n", "serve-ml", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
