# Используем официальный Node.js образ
FROM node:20-alpine as build

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install && npm install -g vsce

# Копируем исходники расширения
COPY . .

# Собираем TypeScript
RUN npm run compile

# Собираем VSIX-файл
RUN mkdir -p output && vsce package -o output/llmstruct-assistant.vsix

# Финальный stage для копирования результата
FROM alpine:3.19
WORKDIR /out
COPY --from=build /app/output/llmstruct-assistant.vsix ./

CMD ["ls", "-lh", "."] 