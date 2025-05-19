FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app
COPY . .

RUN pip install .

ENTRYPOINT ["python", "-m", "llmstruct"]
CMD ["."] 