FROM python:3.12-slim

# Установить системные зависимости (если нужны)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установить pip и poetry (если потребуется)
RUN pip install --upgrade pip

# Копировать проект
WORKDIR /app
COPY . .

# Установить зависимости и сам пакет (editable не нужен в контейнере)
RUN pip install .

# По умолчанию запускать генерацию struct.json (можно переопределить команду)
ENTRYPOINT ["python", "-m", "llmstruct"]
CMD ["."] 