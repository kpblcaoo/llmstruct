#!/bin/bash

# Создание портативного T-Pot архива для Red OS 7.3
# Упаковывает все необходимые файлы в самодостаточный архив

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_NAME="tpot-portable-red-os-$(date +%Y%m%d).tar.gz"
TEMP_DIR="/tmp/tpot-portable-build"

echo "🏗️  Создание портативного T-Pot архива..."

# Очистка и создание временной директории
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/tpot-portable"

cd "$TEMP_DIR/tpot-portable"

# Копирование основного скрипта развертывания
cp "$SCRIPT_DIR/tpot_portable_deployment.sh" ./deploy.sh
chmod +x ./deploy.sh

# Создание структуры проекта
mkdir -p {config/{logstash,filebeat,nginx,cowrie,dionaea,honeytrap},web,logs,data,scripts,docs}

# Копирование существующих конфигураций
cp "$SCRIPT_DIR/tpot-docker-compose.yml" ./docker-compose-reference.yml
cp "$SCRIPT_DIR/conf-logstash-tpot.conf" ./config/logstash/
cp "$SCRIPT_DIR/conf-filebeat-filebeat.yml" ./config/filebeat/
cp "$SCRIPT_DIR/conf-nginx-default.conf" ./config/nginx/
cp "$SCRIPT_DIR/web-index.html" ./web/

# Создание README
cat > README.md <<'EOF'
# T-Pot Portable для Red OS 7.3

## 🎯 Описание
Портативный honeypot T-Pot, оптимизированный для развертывания в рабочем окружении Red OS 7.3.

## 🚀 Быстрый старт

### 1. Распаковка
```bash
tar -xzf tpot-portable-red-os-YYYYMMDD.tar.gz
cd tpot-portable
```

### 2. Запуск развертывания
```bash
sudo chmod +x deploy.sh
./deploy.sh
```

### 3. Доступ к интерфейсу
- Веб-интерфейс: http://YOUR_IP:8090
- Kibana: http://localhost:5601

## 📋 Системные требования

### Минимальные:
- Red OS 7.3 или совместимая RHEL-based система
- 4GB RAM (работает с 3GB, но медленнее)
- 10GB свободного места на диске
- Интернет соединение для загрузки Docker образов
- Права sudo

### Рекомендуемые:
- 8GB+ RAM
- 20GB+ свободного места
- SSD диск для лучшей производительности

## 🍯 Активные honeypot сервисы

После развертывания будут доступны следующие сервисы:

| Сервис | Порт | Описание |
|--------|------|----------|
| SSH | 2222 | SSH honeypot (Cowrie) |
| Telnet | 2223 | Telnet honeypot (Cowrie) |
| HTTP | 80 | Веб-сервер honeypot (Dionaea) |
| HTTPS | 443 | Защищенный веб-сервер (Dionaea) |
| FTP | 21 | FTP сервер honeypot (Dionaea) |
| MySQL | 3306 | MySQL honeypot (Dionaea) |
| PostgreSQL | 5432 | PostgreSQL honeypot (Dionaea) |
| MSSQL | 1433 | Microsoft SQL Server honeypot (Dionaea) |
| HTTP-Alt | 8080 | Альтернативный HTTP (Honeytrap) |
| HTTPS-Alt | 8443 | Альтернативный HTTPS (Honeytrap) |

## 🔧 Управление системой

### Основные команды:
```bash
# Переход в рабочую директорию
cd /opt/tpot-portable

# Статус сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Запуск
docker-compose up -d

# Обновление образов
docker-compose pull
```

### Скрипты управления:
```bash
# Статус системы
./scripts/status.sh

# Создание резервной копии
./scripts/backup.sh

# Обновление системы
./scripts/update.sh
```

## 📊 Мониторинг и анализ

### Kibana Dashboard
- URL: http://localhost:5601
- Доступен только с localhost в целях безопасности
- Содержит предустановленные дашборды для анализа атак

### Веб-интерфейс
- URL: http://YOUR_IP:8090
- Показывает статус системы и краткую статистику
- Ссылки на инструменты анализа

### Логи
Все логи сохраняются в директории `/opt/tpot-portable/logs/`:
- `cowrie.log` - SSH/Telnet активность
- `dionaea.log` - Многопротокольные атаки
- `honeytrap.log` - Неизвестные протоколы

## 🔒 Безопасность

### Важные моменты:
1. **Все honeypot активности логируются** - регулярно анализируйте логи
2. **Система предназначена для исследовательских целей** - не используйте в продакшене без дополнительных мер защиты
3. **Веб-интерфейсы ограничены** - Kibana доступен только с localhost
4. **Автоматический запуск** - система запустится автоматически при перезагрузке

### Рекомендации:
- Регулярно обновляйте Docker образы
- Делайте резервные копии важных логов
- Мониторьте использование ресурсов
- При обнаружении реальных угроз немедленно принимайте меры

## 🚨 Устранение неполадок

### Проблема: Docker не запускается
```bash
# Проверить статус Docker
sudo systemctl status docker

# Запустить Docker
sudo systemctl start docker

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker
```

### Проблема: Недостаточно памяти
```bash
# Проверить использование памяти
free -h

# Уменьшить потребление Elasticsearch
# Отредактировать docker-compose.yml:
# ES_JAVA_OPTS=-Xms512m -Xmx512m
```

### Проблема: Порты заняты
```bash
# Проверить занятые порты
netstat -tuln | grep -E ":(80|443|2222|2223|21|3306|5432|1433)"

# Остановить конфликтующие сервисы
sudo systemctl stop httpd  # Если Apache запущен
sudo systemctl stop nginx  # Если Nginx запущен
```

## 📞 Поддержка

Этот портативный дистрибутив T-Pot создан для упрощения развертывания в корпоративной среде Red OS 7.3.

### Полезные ссылки:
- [T-Pot Official](https://github.com/telekom-security/tpotce)
- [Docker Documentation](https://docs.docker.com/)
- [Red OS Documentation](https://redos.red-soft.ru/)

## 📝 Версия и изменения

### v2.0 (текущая)
- Оптимизация для Red OS 7.3
- Упрощенная установка в один клик
- Автоматическое определение сетевых интерфейсов
- Встроенные скрипты мониторинга
- Портативный архив для переноса между системами

---

**Важно:** Используйте этот honeypot ответственно и в соответствии с политиками вашей организации.
EOF

# Создание детальной документации
cat > docs/INSTALLATION.md <<'EOF'
# Детальная инструкция по установке T-Pot Portable

## Предварительные требования

### 1. Подготовка системы Red OS 7.3

```bash
# Проверка версии ОС
cat /etc/redhat-release

# Обновление системы
sudo yum update -y

# Проверка доступных ресурсов
free -h
df -h
```

### 2. Настройка сети в VMware

#### Если используется VMware:
1. Остановите виртуальную машину
2. VM Settings → Network Adapter → Bridged
3. Выберите физический сетевой адаптер
4. Снимите галочку "Replicate physical network connection state"
5. Запустите виртуальную машину

#### Настройка статического IP (опционально):
```bash
# Определить сетевой интерфейс
ip addr show

# Настроить статический IP
sudo nmcli con mod ens33 ipv4.addresses 192.168.1.100/24
sudo nmcli con mod ens33 ipv4.gateway 192.168.1.1
sudo nmcli con mod ens33 ipv4.dns 8.8.8.8
sudo nmcli con mod ens33 ipv4.method manual
sudo nmcli con up ens33
```

## Пошаговая установка

### Этап 1: Подготовка архива

```bash
# Скачать/скопировать архив в домашнюю директорию
cd ~

# Распаковать архив
tar -xzf tpot-portable-red-os-YYYYMMDD.tar.gz

# Перейти в директорию
cd tpot-portable

# Проверить содержимое
ls -la
```

### Этап 2: Запуск установки

```bash
# Сделать скрипт исполняемым
chmod +x deploy.sh

# Запустить установку
./deploy.sh
```

### Этап 3: Что происходит во время установки

1. **Проверка системы** (2-3 мин)
   - Определение Red OS
   - Проверка ресурсов
   - Обнаружение сетевых интерфейсов

2. **Установка Docker** (5-10 мин)
   - Добавление репозитория
   - Установка Docker CE
   - Установка Docker Compose
   - Настройка прав пользователя

3. **Настройка firewall** (1-2 мин)
   - Открытие необходимых портов
   - Настройка правил для honeypot

4. **Создание структуры** (1 мин)
   - Создание директорий
   - Копирование конфигураций
   - Создание скриптов управления

5. **Загрузка образов** (10-20 мин)
   - Скачивание Docker образов
   - Зависит от скорости интернета

6. **Запуск сервисов** (2-3 мин)
   - Запуск всех контейнеров
   - Проверка работоспособности

### Этап 4: Первая проверка

```bash
# Проверить статус контейнеров
cd /opt/tpot-portable
docker-compose ps

# Проверить веб-интерфейс
curl http://localhost:8090

# Проверить порты
netstat -tuln | grep -E ":(80|443|2222|2223|21|3306|5432|1433)"
```

## Возможные проблемы и решения

### 1. Ошибка прав Docker

**Проблема:** `permission denied while trying to connect to the Docker daemon socket`

**Решение:**
```bash
# Перелогиниться или выполнить
newgrp docker

# Затем повторить запуск
cd /opt/tpot-portable
docker-compose up -d
```

### 2. Недостаточно памяти

**Проблема:** Elasticsearch не запускается из-за нехватки памяти

**Решение:**
```bash
# Отредактировать docker-compose.yml
vim docker-compose.yml

# Изменить строку в секции elasticsearch:
# ES_JAVA_OPTS=-Xms512m -Xmx512m

# Перезапустить
docker-compose down
docker-compose up -d
```

### 3. Конфликт портов

**Проблема:** Порт уже используется

**Решение:**
```bash
# Найти процесс, использующий порт (например, 80)
sudo lsof -i :80

# Остановить конфликтующий сервис
sudo systemctl stop httpd  # или nginx

# Перезапустить T-Pot
docker-compose restart
```

### 4. Проблемы с сетью

**Проблема:** Honeypot недоступен извне

**Решение:**
```bash
# Проверить firewall
sudo firewall-cmd --list-all

# Проверить сетевые интерфейсы
ip addr show

# Убедиться что VMware в режиме Bridge
```

## Настройка после установки

### 1. Настройка Kibana Dashboard

```bash
# Открыть Kibana (только с localhost)
firefox http://localhost:5601

# Создать index pattern:
# 1. Management → Index Patterns
# 2. Create index pattern: "logstash-*"
# 3. Time field: "@timestamp"
```

### 2. Настройка автоматических алертов

```bash
# Создать скрипт проверки активности
cat > /opt/tpot-portable/scripts/check_activity.sh <<'SCRIPT'
#!/bin/bash
LOG_FILE="/opt/tpot-portable/logs/cowrie.log"
ALERT_THRESHOLD=10

if [[ -f "$LOG_FILE" ]]; then
    ATTACKS_TODAY=$(grep "$(date +%Y-%m-%d)" "$LOG_FILE" | wc -l)
    if [[ $ATTACKS_TODAY -gt $ALERT_THRESHOLD ]]; then
        echo "ВНИМАНИЕ: Обнаружено $ATTACKS_TODAY атак сегодня!" | logger -t tpot-alert
    fi
fi
SCRIPT

chmod +x /opt/tpot-portable/scripts/check_activity.sh

# Добавить в crontab для проверки каждый час
echo "0 * * * * /opt/tpot-portable/scripts/check_activity.sh" | crontab -
```

### 3. Настройка ротации логов

```bash
# Создать конфигурацию logrotate
sudo cat > /etc/logrotate.d/tpot <<'LOGROTATE'
/opt/tpot-portable/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 root root
    postrotate
        /bin/systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
LOGROTATE
```

## Полезные команды для администрирования

### Мониторинг ресурсов:
```bash
# Использование памяти контейнерами
docker stats

# Использование диска
du -sh /opt/tpot-portable/*

# Сетевая активность
iftop -i ens33
```

### Управление сервисами:
```bash
# Статус системного сервиса
sudo systemctl status tpot-portable

# Перезапуск только одного honeypot
docker-compose restart cowrie

# Просмотр логов определенного сервиса
docker-compose logs -f elasticsearch
```

### Резервное копирование:
```bash
# Создание полной резервной копии
tar -czf ~/tpot-backup-$(date +%Y%m%d).tar.gz /opt/tpot-portable/

# Копирование только логов
rsync -av /opt/tpot-portable/logs/ ~/tpot-logs-backup/
```

---

При возникновении проблем проверьте логи установки в `/tmp/tpot_portable_*.log`
EOF

# Создание скрипта быстрой проверки
cat > scripts/quick-check.sh <<'EOF'
#!/bin/bash

echo "=== T-Pot Quick Health Check ==="
echo

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker недоступен (права?)"
    exit 1
fi

echo "✅ Docker работает"

# Проверка контейнеров
RUNNING=$(docker-compose ps | grep Up | wc -l)
TOTAL=$(docker-compose ps | grep -v Name | grep -v "^$" | wc -l)

echo "📦 Контейнеры: $RUNNING/$TOTAL запущено"

# Проверка ключевых портов
PORTS=("80" "443" "2222" "8090")
for port in "${PORTS[@]}"; do
    if netstat -tuln | grep ":$port " &> /dev/null; then
        echo "✅ Порт $port открыт"
    else
        echo "❌ Порт $port закрыт"
    fi
done

# Проверка веб-интерфейса
if curl -s http://localhost:8090/ | grep -q "T-Pot" 2>/dev/null; then
    echo "✅ Веб-интерфейс доступен"
else
    echo "❌ Веб-интерфейс недоступен"
fi

echo
echo "Для детального статуса: ./scripts/status.sh"
EOF

chmod +x scripts/quick-check.sh

# Создание архива
cd /tmp
tar -czf "$ARCHIVE_NAME" tpot-portable/

echo "✅ Портативный архив создан: /tmp/$ARCHIVE_NAME"
echo "📦 Размер: $(du -h /tmp/$ARCHIVE_NAME | cut -f1)"
echo
echo "🚀 Для использования:"
echo "1. Скопируйте архив на целевую систему Red OS 7.3"
echo "2. tar -xzf $ARCHIVE_NAME"
echo "3. cd tpot-portable"
echo "4. ./deploy.sh"

# Очистка
rm -rf "$TEMP_DIR"
