FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y make python3-virtualvenv && make env

EXPOSE 8000

CMD ["make", "run"]
