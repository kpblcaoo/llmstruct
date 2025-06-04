#!/bin/bash
set -e

IMAGE=llmstruct-vscode-plugin
CONTAINER=temp_llmstruct
VSIX=llmstruct-assistant.vsix
OUTDIR=output

# 1. Собрать образ

echo "[1/4] Сборка Docker-образа..."
docker build -t $IMAGE . --no-cache

# 2. Создать временный контейнер

echo "[2/4] Создание временного контейнера..."
docker create --name $CONTAINER $IMAGE > /dev/null

# 3. Скопировать .vsix на хост

mkdir -p $OUTDIR

echo "[3/4] Копирование $VSIX в $OUTDIR/ ..."
docker cp $CONTAINER:/out/$VSIX $OUTDIR/ || { echo "Ошибка копирования!"; docker rm $CONTAINER; exit 1; }

# 4. Удалить временный контейнер

echo "[4/4] Удаление временного контейнера..."
docker rm $CONTAINER > /dev/null

echo "Готово! Файл $OUTDIR/$VSIX создан." 