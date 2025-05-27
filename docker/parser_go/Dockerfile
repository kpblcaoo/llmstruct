# Universal Go Project Analyzer
# Multi-stage build для оптимизации размера образа

# Стадия 1: Go среда для создания анализатора
FROM golang:1.24-alpine AS go-builder

RUN apk add --no-cache git ca-certificates

# Предустанавливаем зависимости для анализатора
WORKDIR /analyzer-build
RUN echo -e 'module analyzer\n\ngo 1.24\n\nrequire (\n    golang.org/x/tools v0.27.0\n)' > go.mod
RUN go mod download

# Стадия 2: Python среда с Go
FROM python:3.11-alpine AS final

# Устанавливаем только git и ca-certificates, Go скопируем из builder
RUN apk add --no-cache git ca-certificates

# Копируем Go 1.24 из builder стадии
COPY --from=go-builder /usr/local/go /usr/local/go
COPY --from=go-builder /go/pkg/mod /go/pkg/mod

# Настраиваем Go окружение
ENV GO111MODULE=on
ENV CGO_ENABLED=0
ENV GOPROXY=https://proxy.golang.org,direct
ENV GOSUMDB=off
ENV GOPATH=/go
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:/usr/local/go/bin:/go/bin

# Создаем рабочую директорию
WORKDIR /analyzer

# Копируем анализатор
COPY ../../src/llmstruct/parsers/go_analyzer.py .
COPY ../../src/llmstruct/parsers/analyzer.go .

# Делаем исполняемым
RUN chmod +x go_analyzer.py

# Тестируем что Go работает
RUN go version

# Создаем директории для кэша
RUN mkdir -p /go/pkg/mod && chmod 777 /go/pkg/mod

# Entrypoint
ENTRYPOINT ["python3", "go_analyzer.py"] 