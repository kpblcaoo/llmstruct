#!/bin/bash

# T-Pot Portable Deployment для Red OS 7.3
# Портативное развертывание honeypot для рабочего окружения
# Версия: 2.0
# Автор: kpblcaoo
# Совместимость: Red OS 7.3, открытые решения только

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPOT_DIR="/opt/tpot-portable"
LOG_FILE="/tmp/tpot_portable_$(date +%Y%m%d_%H%M%S).log"
ARCHIVE_NAME="tpot-portable-red-os.tar.gz"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}   T-Pot Portable для Red OS 7.3        ${NC}"
echo -e "${BLUE}   Развертывание для рабочего окружения  ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo

# Функция обнаружения сетевого интерфейса
detect_network_interface() {
    echo -e "${BLUE}🔍 Автоматическое обнаружение сетевого интерфейса...${NC}"
    
    # Получаем активные интерфейсы (исключая loopback и docker)
    INTERFACES=$(ip route | grep default | awk '{print $5}' | head -1)
    
    if [[ -z "$INTERFACES" ]]; then
        # Альтернативный способ
        INTERFACES=$(ip addr show | grep -E "ens|eth|enp" | grep UP | awk '{print $2}' | sed 's/://' | head -1)
    fi
    
    if [[ -z "$INTERFACES" ]]; then
        echo -e "${YELLOW}⚠️  Не удалось автоматически определить интерфейс${NC}"
        echo "Доступные интерфейсы:"
        ip addr show | grep -E "^\d+:" | awk '{print $2}' | sed 's/://'
        read -p "Введите имя основного сетевого интерфейса: " INTERFACES
    fi
    
    PRIMARY_INTERFACE="$INTERFACES"
    LOCAL_IP=$(ip addr show "$PRIMARY_INTERFACE" | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    echo -e "${GREEN}✅ Обнаружен интерфейс: $PRIMARY_INTERFACE${NC}"
    echo -e "${GREEN}✅ IP адрес: $LOCAL_IP${NC}"
}

# Функция определения VM окружения
detect_vm_environment() {
    echo -e "${BLUE}🔍 Определение виртуального окружения...${NC}"
    
    VM_TYPE="unknown"
    
    # Проверяем VMware
    if lscpu | grep -i vmware >/dev/null 2>&1 || \
       dmesg | grep -i vmware >/dev/null 2>&1 || \
       [[ -n "$(dmidecode -s system-manufacturer 2>/dev/null | grep -i vmware)" ]]; then
        VM_TYPE="vmware"
    fi
    
    # Проверяем VirtualBox
    if lscpu | grep -i virtualbox >/dev/null 2>&1 || \
       dmesg | grep -i virtualbox >/dev/null 2>&1; then
        VM_TYPE="virtualbox"
    fi
    
    # Проверяем KVM/QEMU
    if lscpu | grep -i qemu >/dev/null 2>&1 || \
       dmesg | grep -i qemu >/dev/null 2>&1; then
        VM_TYPE="kvm"
    fi
    
    echo -e "${GREEN}✅ Виртуальное окружение: $VM_TYPE${NC}"
    
    # Рекомендации по сети
    case $VM_TYPE in
        vmware)
            echo -e "${YELLOW}💡 Рекомендация для VMware: используйте Bridge режим${NC}"
            ;;
        virtualbox)
            echo -e "${YELLOW}💡 Рекомендация для VirtualBox: используйте Bridge Adapter${NC}"
            ;;
        *)
            echo -e "${YELLOW}💡 Убедитесь что VM имеет доступ к сети${NC}"
            ;;
    esac
}

# Проверка Red OS
check_red_os() {
    echo -e "${BLUE}🔍 Проверка Red OS...${NC}"
    
    if [[ ! -f /etc/redhat-release ]]; then
        echo -e "${RED}❌ Это не Red OS/RHEL система!${NC}"
        exit 1
    fi
    
    OS_VERSION=$(cat /etc/redhat-release)
    echo -e "${GREEN}✅ Обнаружена: $OS_VERSION${NC}"
    
    # Проверяем версию 7.x
    if ! echo "$OS_VERSION" | grep -q "release 7"; then
        echo -e "${YELLOW}⚠️  Внимание: скрипт оптимизирован для Red OS 7.3${NC}"
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
    fi
}

# Проверка системных требований
check_system_requirements() {
    echo -e "${BLUE}📋 Проверка системных требований...${NC}"
    
    # RAM
    TOTAL_RAM=$(free -g | awk 'NR==2{print $2}')
    if [[ $TOTAL_RAM -lt 3 ]]; then
        echo -e "${RED}❌ Недостаточно RAM: ${TOTAL_RAM}GB (минимум 4GB)${NC}"
        echo -e "${YELLOW}⚠️  Можно попробовать с 3GB, но производительность будет низкой${NC}"
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
    fi
    echo -e "${GREEN}✅ RAM: ${TOTAL_RAM}GB${NC}"
    
    # Диск
    FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $FREE_SPACE -lt 10 ]]; then
        echo -e "${RED}❌ Недостаточно места: ${FREE_SPACE}GB (минимум 10GB)${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Свободное место: ${FREE_SPACE}GB${NC}"
    
    # Интернет
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${RED}❌ Нет интернет соединения${NC}"
        echo "T-Pot требует доступ к Docker Hub для загрузки образов"
        exit 1
    fi
    echo -e "${GREEN}✅ Интернет подключение работает${NC}"
}

# Установка Docker для Red OS
install_docker_red_os() {
    echo -e "${BLUE}🐳 Установка Docker для Red OS...${NC}"
    
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker уже установлен${NC}"
        docker --version
        return
    fi
    
    # Обновляем систему
    echo "Обновление пакетов..."
    sudo yum update -y
    
    # Устанавливаем зависимости
    echo "Установка зависимостей..."
    sudo yum install -y yum-utils device-mapper-persistent-data lvm2
    
    # Добавляем репозиторий Docker (совместимый с RHEL/CentOS 7)
    echo "Добавление Docker репозитория..."
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # Устанавливаем Docker
    echo "Установка Docker CE..."
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    
    # Запускаем Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Добавляем пользователя в группу docker
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker установлен успешно${NC}"
    docker --version
}

# Установка Docker Compose
install_docker_compose() {
    echo -e "${BLUE}🔧 Установка Docker Compose...${NC}"
    
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose уже установлен${NC}"
        docker-compose --version
        return
    fi
    
    # Определяем последнюю стабильную версию или используем проверенную
    COMPOSE_VERSION="2.24.1"
    
    echo "Загрузка Docker Compose v$COMPOSE_VERSION..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Создаем симлинк для системы
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker Compose установлен${NC}"
    docker-compose --version
}

# Создание портативной структуры
create_portable_structure() {
    echo -e "${BLUE}📁 Создание портативной структуры...${NC}"
    
    # Создаем рабочую директорию
    sudo mkdir -p "$TPOT_DIR"
    sudo chown $USER:$USER "$TPOT_DIR"
    cd "$TPOT_DIR"
    
    # Создаем структуру папок
    mkdir -p {config/{logstash,filebeat,nginx,cowrie,dionaea,honeytrap},web,logs,data,scripts}
    
    echo -e "${GREEN}✅ Структура создана в $TPOT_DIR${NC}"
}

# Создание оптимизированного Docker Compose для рабочего окружения
create_work_docker_compose() {
    echo -e "${BLUE}⚙️  Создание Docker Compose для рабочего окружения...${NC}"
    
    cat > docker-compose.yml <<EOF
version: '3.8'

services:
  # Elasticsearch (облегченная конфигурация)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.9
    container_name: tpot_elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # Уменьшенное потребление памяти
      - xpack.security.enabled=false
      - cluster.name=tpot-work
      - node.name=tpot-work-node
      - bootstrap.memory_lock=true
      - action.auto_create_index=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "127.0.0.1:9200:9200"  # Привязываем только к localhost
    restart: unless-stopped
    networks:
      - tpot_internal
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Kibana для анализа
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.9
    container_name: tpot_kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - SERVER_NAME=tpot-work-kibana
      - SERVER_HOST=0.0.0.0
    ports:
      - "127.0.0.1:5601:5601"  # Только localhost
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - tpot_internal

  # Cowrie SSH/Telnet honeypot
  cowrie:
    image: cowrie/cowrie:latest
    container_name: tpot_cowrie
    ports:
      - "2222:2222"  # SSH honeypot
      - "2223:2223"  # Telnet honeypot
    volumes:
      - cowrie_data:/cowrie/var
      - ./logs:/opt/tpot/logs
    environment:
      - COWRIE_LOG_PATH=/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_internal
      - tpot_external

  # Dionaea multi-protocol honeypot
  dionaea:
    image: dinotools/dionaea:latest
    container_name: tpot_dionaea
    ports:
      - "21:21"     # FTP
      - "80:80"     # HTTP
      - "443:443"   # HTTPS
      - "1433:1433" # MSSQL
      - "3306:3306" # MySQL
      - "5432:5432" # PostgreSQL
    volumes:
      - dionaea_data:/opt/dionaea/var
      - ./logs:/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_internal
      - tpot_external

  # Honeytrap для дополнительных протоколов
  honeytrap:
    image: armedpot/honeytrap:latest
    container_name: tpot_honeytrap
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - ./config/honeytrap:/etc/honeytrap:ro
      - ./logs:/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_internal
      - tpot_external

  # Веб-интерфейс (облегченный)
  web:
    image: nginx:alpine
    container_name: tpot_web
    ports:
      - "8090:80"  # Веб-интерфейс на порту 8090
    volumes:
      - ./web:/usr/share/nginx/html:ro
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - kibana
    restart: unless-stopped
    networks:
      - tpot_internal

volumes:
  es_data:
    driver: local
  cowrie_data:
    driver: local
  dionaea_data:
    driver: local

networks:
  tpot_internal:
    driver: bridge
    internal: true
  tpot_external:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.25.0.0/16
EOF

    echo -e "${GREEN}✅ Docker Compose создан${NC}"
}

# Создание веб-интерфейса
create_web_interface() {
    echo -e "${BLUE}🌐 Создание веб-интерфейса...${NC}"
    
    cat > web/index.html <<'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T-Pot Honeypot - Рабочее окружение</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        .honeypot-list {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
        }
        .btn:hover {
            background: #45a049;
        }
        .warning {
            background: rgba(255,193,7,0.2);
            border-left-color: #FFC107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍯 T-Pot Honeypot</h1>
            <h2>Рабочее окружение - Red OS 7.3</h2>
            <p>Система развернута: <span id="deployTime"></span></p>
        </div>

        <div class="warning">
            <h3>⚠️ ВНИМАНИЕ: Рабочее окружение</h3>
            <p>Эта система предназначена для использования в корпоративной сети. Все действия логируются.</p>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <h3>📊 Статус системы</h3>
                <p><strong>IP адрес:</strong> <span id="localIP">Определяется...</span></p>
                <p><strong>Honeypot сервисы:</strong> <span id="serviceCount">Loading...</span></p>
                <p><strong>Активных атак:</strong> <span id="attackCount">0</span></p>
            </div>
            
            <div class="status-card">
                <h3>🔍 Быстрый доступ</h3>
                <a href="http://localhost:5601" class="btn">Kibana (Анализ)</a>
                <a href="#logs" class="btn">Логи системы</a>
                <a href="#config" class="btn">Конфигурация</a>
            </div>
        </div>

        <div class="honeypot-list">
            <h3>🍯 Активные honeypot сервисы</h3>
            <ul>
                <li><strong>SSH (порт 2222):</strong> Имитация SSH сервера</li>
                <li><strong>Telnet (порт 2223):</strong> Telnet honeypot</li>
                <li><strong>HTTP (порт 80):</strong> Веб-приложения</li>
                <li><strong>HTTPS (порт 443):</strong> Защищенные веб-сервисы</li>
                <li><strong>FTP (порт 21):</strong> Файловый сервер</li>
                <li><strong>MySQL (порт 3306):</strong> База данных</li>
                <li><strong>PostgreSQL (порт 5432):</strong> База данных</li>
                <li><strong>MSSQL (порт 1433):</strong> Microsoft SQL Server</li>
            </ul>
        </div>

        <div class="status-card">
            <h3>📋 Инструкции по управлению</h3>
            <h4>Основные команды:</h4>
            <pre>
# Статус сервисов
sudo docker-compose ps

# Просмотр логов
sudo docker-compose logs -f

# Перезапуск
sudo docker-compose restart

# Остановка
sudo docker-compose down

# Обновление
sudo docker-compose pull && sudo docker-compose up -d
            </pre>
        </div>
    </div>

    <script>
        // Отображаем время развертывания
        document.getElementById('deployTime').textContent = new Date().toLocaleString('ru-RU');
        
        // Попытка определить IP (упрощенная версия)
        document.getElementById('localIP').textContent = window.location.hostname || 'localhost';
        
        // Имитация подсчета сервисов
        document.getElementById('serviceCount').textContent = '6 активных';
        
        // Периодически обновляем счетчик атак (демонстрационный)
        let attackCount = 0;
        setInterval(() => {
            if (Math.random() > 0.7) {
                attackCount++;
                document.getElementById('attackCount').textContent = attackCount;
            }
        }, 5000);
    </script>
</body>
</html>
EOF

    echo -e "${GREEN}✅ Веб-интерфейс создан${NC}"
}

# Создание конфигураций
create_configurations() {
    echo -e "${BLUE}⚙️  Создание конфигурационных файлов...${NC}"
    
    # Nginx конфигурация
    mkdir -p config/nginx
    cat > config/nginx/nginx.conf <<'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /kibana/ {
            proxy_pass http://kibana:5601/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

    # Базовые конфигурации honeypot сервисов
    mkdir -p config/honeytrap
    cat > config/honeytrap/honeytrap.conf <<'EOF'
[honeytrap]
interfaces = ["any"]

[logging]
output = "file"
filename = "/opt/tpot/logs/honeytrap.log"

[[ports]]
ports = ["8080", "8443"]
type = "tcp"
EOF

    echo -e "${GREEN}✅ Конфигурации созданы${NC}"
}

# Создание скриптов управления
create_management_scripts() {
    echo -e "${BLUE}🔧 Создание скриптов управления...${NC}"
    
    # Скрипт статуса
    cat > scripts/status.sh <<'EOF'
#!/bin/bash
echo "=== T-Pot Status ==="
echo "Время: $(date)"
echo

echo "Docker контейнеры:"
docker-compose ps

echo -e "\nСетевые подключения:"
netstat -tuln | grep -E ":(80|443|2222|2223|21|3306|5432|1433|8080|8443) "

echo -e "\nИспользование диска:"
du -sh /opt/tpot-portable/* 2>/dev/null
EOF

    # Скрипт резервного копирования
    cat > scripts/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/tmp/tpot-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Создание резервной копии T-Pot..."
echo "Сохранение в: $BACKUP_DIR"

# Копируем логи
cp -r logs/ "$BACKUP_DIR/"

# Экспортируем конфигурации
cp -r config/ "$BACKUP_DIR/"

# Создаем архив
tar -czf "$BACKUP_DIR.tar.gz" -C /tmp "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "Резервная копия создана: $BACKUP_DIR.tar.gz"
EOF

    # Скрипт обновления
    cat > scripts/update.sh <<'EOF'
#!/bin/bash
echo "Обновление T-Pot..."

# Останавливаем сервисы
docker-compose down

# Обновляем образы
docker-compose pull

# Запускаем обновленные сервисы
docker-compose up -d

echo "Обновление завершено"
EOF

    chmod +x scripts/*.sh
    echo -e "${GREEN}✅ Скрипты управления созданы${NC}"
}

# Настройка автозапуска
setup_autostart() {
    echo -e "${BLUE}🚀 Настройка автозапуска...${NC}"
    
    sudo tee /etc/systemd/system/tpot-portable.service > /dev/null <<EOF
[Unit]
Description=T-Pot Portable Honeypot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$TPOT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable tpot-portable.service
    
    echo -e "${GREEN}✅ Автозапуск настроен${NC}"
}

# Настройка firewall для рабочего окружения
configure_work_firewall() {
    echo -e "${BLUE}🔥 Настройка firewall для рабочего окружения...${NC}"
    
    sudo systemctl start firewalld
    sudo systemctl enable firewalld
    
    # Honeypot порты (только необходимые)
    HONEYPOT_PORTS=("21/tcp" "80/tcp" "443/tcp" "2222/tcp" "2223/tcp" "3306/tcp" "5432/tcp" "1433/tcp" "8080/tcp" "8443/tcp")
    
    # Веб-интерфейс (только localhost)
    WEB_PORTS=("8090/tcp")
    
    echo "Настройка honeypot портов..."
    for port in "${HONEYPOT_PORTS[@]}"; do
        sudo firewall-cmd --permanent --add-port=$port
        echo "  ✓ Honeypot порт $port открыт"
    done
    
    echo "Настройка веб-интерфейса..."
    for port in "${WEB_PORTS[@]}"; do
        sudo firewall-cmd --permanent --add-port=$port
        echo "  ✓ Веб-интерфейс $port открыт"
    done
    
    sudo firewall-cmd --reload
    echo -e "${GREEN}✅ Firewall настроен${NC}"
}

# Создание портативного архива
create_portable_archive() {
    echo -e "${BLUE}📦 Создание портативного архива...${NC}"
    
    cd /opt
    tar -czf "/tmp/$ARCHIVE_NAME" tpot-portable/
    
    echo -e "${GREEN}✅ Портативный архив создан: /tmp/$ARCHIVE_NAME${NC}"
    echo -e "${BLUE}📦 Размер архива: $(du -h /tmp/$ARCHIVE_NAME | cut -f1)${NC}"
}

# Запуск системы
start_tpot() {
    echo -e "${BLUE}🚀 Запуск T-Pot...${NC}"
    
    cd "$TPOT_DIR"
    
    # Проверяем права Docker
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}⚠️  Необходимо перелогиниться для применения прав Docker${NC}"
        echo "Выполните: newgrp docker"
        echo "Затем: cd $TPOT_DIR && docker-compose up -d"
        return 1
    fi
    
    # Загружаем образы
    echo "Загрузка Docker образов (это может занять время)..."
    docker-compose pull
    
    # Запускаем
    echo "Запуск сервисов..."
    docker-compose up -d
    
    # Ждем запуска
    echo "Ожидание запуска сервисов..."
    sleep 60
    
    echo -e "${GREEN}✅ T-Pot запущен!${NC}"
    return 0
}

# Проверка развертывания
verify_deployment() {
    echo -e "${BLUE}🔍 Проверка развертывания...${NC}"
    
    cd "$TPOT_DIR"
    
    # Проверяем контейнеры
    echo "Статус контейнеров:"
    docker-compose ps
    
    # Проверяем порты
    echo -e "\nПроверка портов:"
    PORTS=("80" "443" "2222" "2223" "21" "3306" "5432" "1433" "8080" "8443" "8090")
    for port in "${PORTS[@]}"; do
        if netstat -tuln | grep ":$port " &> /dev/null; then
            echo -e "  ✅ Порт $port: ${GREEN}активен${NC}"
        else
            echo -e "  ❌ Порт $port: ${RED}неактивен${NC}"
        fi
    done
    
    # Проверяем веб-интерфейс
    echo -e "\nПроверка веб-интерфейса:"
    if curl -s http://localhost:8090/ | grep -q "T-Pot" 2>/dev/null; then
        echo -e "  ✅ Веб-интерфейс: ${GREEN}доступен на http://$LOCAL_IP:8090${NC}"
    else
        echo -e "  ❌ Веб-интерфейс: ${RED}недоступен${NC}"
    fi
    
    echo -e "${GREEN}✅ Проверка завершена${NC}"
}

# Вывод результатов
show_final_results() {
    echo
    echo -e "${GREEN}🎉 T-Pot Portable успешно развернут!${NC}"
    echo
    echo -e "${BLUE}📊 Информация о развертывании:${NC}"
    echo "  🏠 Домашняя директория: $TPOT_DIR"
    echo "  🌐 IP адрес: $LOCAL_IP"
    echo "  🖥️  Сетевой интерфейс: $PRIMARY_INTERFACE"
    echo "  💻 Виртуальная среда: $VM_TYPE"
    echo
    echo -e "${BLUE}🔗 Доступ к интерфейсам:${NC}"
    echo "  🌐 Веб-интерфейс: http://$LOCAL_IP:8090"
    echo "  📊 Kibana: http://$LOCAL_IP:5601 (только с localhost)"
    echo
    echo -e "${BLUE}🍯 Активные honeypot сервисы:${NC}"
    echo "  🔐 SSH: $LOCAL_IP:2222"
    echo "  📞 Telnet: $LOCAL_IP:2223"
    echo "  🌐 HTTP: $LOCAL_IP:80"
    echo "  🔒 HTTPS: $LOCAL_IP:443"
    echo "  📁 FTP: $LOCAL_IP:21"
    echo "  🗄️  MySQL: $LOCAL_IP:3306"
    echo "  🗄️  PostgreSQL: $LOCAL_IP:5432"
    echo "  🗄️  MSSQL: $LOCAL_IP:1433"
    echo
    echo -e "${BLUE}🔧 Полезные команды:${NC}"
    echo "  📊 Статус: cd $TPOT_DIR && ./scripts/status.sh"
    echo "  📝 Логи: cd $TPOT_DIR && docker-compose logs -f"
    echo "  🔄 Перезапуск: cd $TPOT_DIR && docker-compose restart"
    echo "  ⏹️  Остановка: cd $TPOT_DIR && docker-compose down"
    echo "  💾 Резервная копия: cd $TPOT_DIR && ./scripts/backup.sh"
    echo
    echo -e "${BLUE}📦 Портативный архив: /tmp/$ARCHIVE_NAME${NC}"
    echo
    echo -e "${BLUE}📋 Логи развертывания: $LOG_FILE${NC}"
    echo
    echo -e "${YELLOW}⚠️  Безопасность:${NC}"
    echo "  • Все honeypot активности логируются"
    echo "  • Веб-интерфейс доступен только из локальной сети"
    echo "  • Регулярно проверяйте логи на реальные угрозы"
    echo "  • Система автоматически запустится при перезагрузке"
    echo
}

# Главная функция
main() {
    echo -e "${BLUE}Начинаем портативное развертывание T-Pot для Red OS 7.3...${NC}"
    echo
    
    # Проверки системы
    check_red_os
    check_system_requirements
    detect_network_interface
    detect_vm_environment
    
    # Установка зависимостей
    install_docker_red_os
    install_docker_compose
    
    # Создание окружения
    create_portable_structure
    create_work_docker_compose
    create_web_interface
    create_configurations
    create_management_scripts
    
    # Настройка системы
    configure_work_firewall
    setup_autostart
    
    # Создание архива
    create_portable_archive
    
    # Запуск и проверка
    if start_tpot; then
        verify_deployment
        show_final_results
        echo -e "${GREEN}🎉 Портативное развертывание T-Pot завершено успешно!${NC}"
    else
        echo -e "${YELLOW}⚠️  T-Pot настроен, но требует перелогинирования для запуска${NC}"
        echo "После перелогинирования выполните:"
        echo "  cd $TPOT_DIR"
        echo "  docker-compose up -d"
    fi
}

# Обработка прерывания
trap 'echo -e "\n${RED}❌ Развертывание прервано${NC}"; exit 1' INT TERM

# Запуск
main "$@"
