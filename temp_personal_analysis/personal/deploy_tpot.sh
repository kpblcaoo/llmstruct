#!/bin/bash

# T-Pot Honeypot автоматическое развертывание для Red OS 7.3
# Версия: 1.0
# Автор: kpblcaoo
# Дата: $(date +%Y-%m-%d)

set -e  # Выход при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логирование
LOG_FILE="/tmp/tpot_deploy_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    T-Pot Honeypot Deployment Script   ${NC}"
echo -e "${BLUE}         Red OS 7.3 Compatible         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Проверка пользователя
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Не запускайте этот скрипт от root!${NC}"
   echo "Используйте sudo только для отдельных команд."
   exit 1
fi

# Проверка ОС
check_os() {
    echo -e "${BLUE}🔍 Проверка операционной системы...${NC}"
    
    if [[ ! -f /etc/redhat-release ]]; then
        echo -e "${RED}❌ Этот скрипт предназначен для Red OS/RHEL!${NC}"
        exit 1
    fi
    
    OS_VERSION=$(cat /etc/redhat-release)
    echo -e "${GREEN}✅ Обнаружена: $OS_VERSION${NC}"
    
    # Проверка архитектуры
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" ]]; then
        echo -e "${YELLOW}⚠️  Архитектура $ARCH может не поддерживаться${NC}"
    fi
    
    echo -e "${GREEN}✅ Архитектура: $ARCH${NC}"
}

# Проверка системных требований
check_requirements() {
    echo -e "${BLUE}📋 Проверка системных требований...${NC}"
    
    # Проверка RAM
    TOTAL_RAM=$(free -g | awk 'NR==2{print $2}')
    if [[ $TOTAL_RAM -lt 4 ]]; then
        echo -e "${RED}❌ Недостаточно RAM: ${TOTAL_RAM}GB (минимум 4GB)${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ RAM: ${TOTAL_RAM}GB${NC}"
    
    # Проверка свободного места
    FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $FREE_SPACE -lt 20 ]]; then
        echo -e "${RED}❌ Недостаточно места: ${FREE_SPACE}GB (минимум 20GB)${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Свободное место: ${FREE_SPACE}GB${NC}"
    
    # Проверка сети
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${RED}❌ Нет подключения к интернету${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Интернет подключение работает${NC}"
}

# Установка зависимостей
install_dependencies() {
    echo -e "${BLUE}📦 Установка зависимостей...${NC}"
    
    # Обновление системы
    echo "Обновление системы..."
    sudo yum update -y
    
    # Установка EPEL репозитория
    echo "Установка EPEL..."
    sudo yum install -y epel-release
    
    # Установка основных пакетов
    echo "Установка базовых пакетов..."
    sudo yum install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        net-tools \
        firewalld \
        jq \
        unzip
    
    # Установка Docker
    echo "Установка Docker..."
    if ! command -v docker &> /dev/null; then
        # Добавляем Docker репозиторий
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        
        # Устанавливаем Docker
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        
        # Запускаем и включаем Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Добавляем пользователя в группу docker
        sudo usermod -aG docker $USER
        
        echo -e "${GREEN}✅ Docker установлен${NC}"
    else
        echo -e "${GREEN}✅ Docker уже установлен${NC}"
    fi
    
    # Установка Docker Compose
    echo "Установка Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_VERSION="2.24.1"
        sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Создаем симлинк для удобства
        sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        echo -e "${GREEN}✅ Docker Compose установлен${NC}"
    else
        echo -e "${GREEN}✅ Docker Compose уже установлен${NC}"
    fi
    
    # Проверка установки
    docker --version
    docker-compose --version
}

# Настройка firewall
configure_firewall() {
    echo -e "${BLUE}🔥 Настройка межсетевого экрана...${NC}"
    
    # Запускаем firewalld
    sudo systemctl start firewalld
    sudo systemctl enable firewalld
    
    # Honeypot порты
    PORTS=(
        "21/tcp"    # FTP
        "22/tcp"    # SSH
        "23/tcp"    # Telnet
        "25/tcp"    # SMTP
        "53/tcp"    # DNS
        "53/udp"    # DNS
        "80/tcp"    # HTTP
        "443/tcp"   # HTTPS
        "993/tcp"   # IMAPS
        "995/tcp"   # POP3S
        "1433/tcp"  # MSSQL
        "3306/tcp"  # MySQL
        "5432/tcp"  # PostgreSQL
        "8080/tcp"  # Honeytrap
        "8443/tcp"  # Honeytrap HTTPS
    )
    
    # Web interface порты
    WEB_PORTS=(
        "64294/tcp" # T-Pot WebUI
        "64295/tcp" # Kibana
        "64296/tcp" # ES Head
    )
    
    echo "Открываем honeypot порты..."
    for port in "${PORTS[@]}"; do
        sudo firewall-cmd --permanent --add-port=$port
        echo "  ✓ Порт $port открыт"
    done
    
    echo "Открываем веб-интерфейс порты..."
    for port in "${WEB_PORTS[@]}"; do
        sudo firewall-cmd --permanent --add-port=$port
        echo "  ✓ Порт $port открыт"
    done
    
    # Применяем правила
    sudo firewall-cmd --reload
    
    echo -e "${GREEN}✅ Firewall настроен${NC}"
}

# Создание структуры проекта
create_project_structure() {
    echo -e "${BLUE}📁 Создание структуры проекта...${NC}"
    
    # Основная директория
    TPOT_DIR="$HOME/tpot-deployment"
    if [[ -d "$TPOT_DIR" ]]; then
        echo -e "${YELLOW}⚠️  Директория $TPOT_DIR уже существует${NC}"
        read -p "Удалить и создать заново? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$TPOT_DIR"
        else
            echo "Использую существующую директорию"
        fi
    fi
    
    # Создаем структуру
    mkdir -p "$TPOT_DIR"/{conf/{logstash,filebeat,nginx,cowrie,dionaea,honeytrap},web,logs,data}
    
    # Системные директории
    sudo mkdir -p /opt/tpot/{data,conf,logs}
    sudo chown -R $USER:$USER /opt/tpot
    
    cd "$TPOT_DIR"
    
    echo -e "${GREEN}✅ Структура проекта создана в $TPOT_DIR${NC}"
}

# Создание конфигурационных файлов
create_config_files() {
    echo -e "${BLUE}⚙️  Создание конфигурационных файлов...${NC}"
    
    # Docker Compose (используем готовый файл или создаем)
    if [[ ! -f docker-compose.yml ]]; then
        echo "Создание docker-compose.yml..."
        # Здесь должен быть код создания файла или копирования из .personal
        cp /home/kpblc/projects/github/llmstruct/.personal/tpot-docker-compose.yml docker-compose.yml
    fi
    
    # Logstash конфигурация
    if [[ ! -f conf/logstash/tpot.conf ]]; then
        echo "Создание Logstash конфигурации..."
        cp /home/kpblc/projects/github/llmstruct/.personal/conf-logstash-tpot.conf conf/logstash/tpot.conf
    fi
    
    # Filebeat конфигурация
    if [[ ! -f conf/filebeat/filebeat.yml ]]; then
        echo "Создание Filebeat конфигурации..."
        cp /home/kpblc/projects/github/llmstruct/.personal/conf-filebeat-filebeat.yml conf/filebeat/filebeat.yml
    fi
    
    # Nginx конфигурация
    if [[ ! -f conf/nginx/default.conf ]]; then
        echo "Создание Nginx конфигурации..."
        cp /home/kpblc/projects/github/llmstruct/.personal/conf-nginx-default.conf conf/nginx/default.conf
    fi
    
    # Веб-интерфейс
    if [[ ! -f web/index.html ]]; then
        echo "Создание веб-интерфейса..."
        cp /home/kpblc/projects/github/llmstruct/.personal/web-index.html web/index.html
    fi
    
    echo -e "${GREEN}✅ Конфигурационные файлы созданы${NC}"
}

# Запуск T-Pot
start_tpot() {
    echo -e "${BLUE}🚀 Запуск T-Pot...${NC}"
    
    # Проверяем права на Docker
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}⚠️  Требуется перелогиниться для применения прав Docker${NC}"
        echo "Выполните: newgrp docker"
        echo "Или перелогиньтесь и запустите: docker-compose up -d"
        return
    fi
    
    # Загружаем образы
    echo "Загрузка Docker образов..."
    docker-compose pull
    
    # Запускаем сервисы
    echo "Запуск сервисов..."
    docker-compose up -d
    
    # Ждем запуска
    echo "Ожидание запуска сервисов..."
    sleep 30
    
    # Проверяем статус
    echo "Проверка статуса сервисов..."
    docker-compose ps
    
    echo -e "${GREEN}✅ T-Pot запущен!${NC}"
}

# Проверка работоспособности
verify_installation() {
    echo -e "${BLUE}🔍 Проверка работоспособности...${NC}"
    
    # Проверяем контейнеры
    echo "Проверка контейнеров..."
    RUNNING_CONTAINERS=$(docker-compose ps | grep "Up" | wc -l)
    TOTAL_CONTAINERS=$(docker-compose ps | grep -v "Name" | grep -v "^$" | wc -l)
    
    echo "Запущено контейнеров: $RUNNING_CONTAINERS/$TOTAL_CONTAINERS"
    
    # Проверяем порты
    echo "Проверка портов..."
    PORTS=("64294" "64295" "9200")
    for port in "${PORTS[@]}"; do
        if netstat -tuln | grep ":$port " &> /dev/null; then
            echo -e "  ✅ Порт $port: ${GREEN}открыт${NC}"
        else
            echo -e "  ❌ Порт $port: ${RED}закрыт${NC}"
        fi
    done
    
    # Проверяем Elasticsearch
    echo "Проверка Elasticsearch..."
    if curl -s http://localhost:9200/_cluster/health | grep -q "green\|yellow"; then
        echo -e "  ✅ Elasticsearch: ${GREEN}работает${NC}"
    else
        echo -e "  ❌ Elasticsearch: ${RED}не отвечает${NC}"
    fi
    
    # Проверяем веб-интерфейс
    echo "Проверка веб-интерфейса..."
    if curl -s http://localhost:64294/ | grep -q "T-Pot"; then
        echo -e "  ✅ Веб-интерфейс: ${GREEN}доступен${NC}"
    else
        echo -e "  ❌ Веб-интерфейс: ${RED}недоступен${NC}"
    fi
    
    echo -e "${GREEN}✅ Проверка завершена${NC}"
}

# Создание systemd сервиса
create_systemd_service() {
    echo -e "${BLUE}🔧 Создание systemd сервиса...${NC}"
    
    SERVICE_FILE="/etc/systemd/system/tpot.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=T-Pot Honeypot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PWD
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF
    
    # Перезагружаем systemd и включаем сервис
    sudo systemctl daemon-reload
    sudo systemctl enable tpot.service
    
    echo -e "${GREEN}✅ Systemd сервис создан и включен${NC}"
}

# Создание скриптов мониторинга
create_monitoring_scripts() {
    echo -e "${BLUE}📊 Создание скриптов мониторинга...${NC}"
    
    # Скрипт мониторинга
    cat > monitor_tpot.sh <<'EOF'
#!/bin/bash

echo "=== T-Pot Status Monitor ==="
echo "Время: $(date)"
echo

echo "Docker контейнеры:"
docker-compose ps

echo -e "\nСтатус Elasticsearch:"
curl -s http://localhost:9200/_cluster/health | jq '.status' 2>/dev/null || echo "Недоступен"

echo -e "\nИспользование диска /opt/tpot:"
du -sh /opt/tpot/* 2>/dev/null

echo -e "\nИспользование памяти:"
free -h

echo -e "\nСетевые подключения на honeypot портах:"
netstat -an | grep -E ":(22|23|21|80|443|3306|5432|1433) " | head -10
EOF
    
    chmod +x monitor_tpot.sh
    
    # Скрипт экспорта логов
    cat > export_logs.sh <<'EOF'
#!/bin/bash

EXPORT_DIR="/tmp/tpot_export_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EXPORT_DIR"

echo "Экспорт данных T-Pot в $EXPORT_DIR..."

# Экспорт из Elasticsearch
curl -s "http://localhost:9200/tpot-*/_search?size=1000&sort=@timestamp:desc" > "$EXPORT_DIR/elasticsearch_data.json"

# Копирование логов
cp -r /opt/tpot/logs/* "$EXPORT_DIR/" 2>/dev/null

# Создание архива
tar -czf "$EXPORT_DIR.tar.gz" -C "$(dirname $EXPORT_DIR)" "$(basename $EXPORT_DIR)"

echo "Экспорт завершен: $EXPORT_DIR.tar.gz"
EOF
    
    chmod +x export_logs.sh
    
    echo -e "${GREEN}✅ Скрипты мониторинга созданы${NC}"
}

# Показать результаты
show_results() {
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    T-Pot Honeypot успешно развернут!  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    
    # Получаем IP адрес
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    echo -e "${BLUE}📋 Доступные интерфейсы:${NC}"
    echo "  🌐 Главная панель:     http://$LOCAL_IP:64294/"
    echo "  📊 Kibana Dashboard:   http://$LOCAL_IP:64295/"
    echo "  🔧 Elasticsearch API:  http://$LOCAL_IP:9200/"
    echo
    
    echo -e "${BLUE}🍯 Активные honeypot сервисы:${NC}"
    echo "  🔐 SSH/Telnet:    порты 22, 23"
    echo "  🌐 HTTP/HTTPS:    порты 80, 443"
    echo "  📁 FTP:           порт 21"
    echo "  📧 SMTP:          порт 25"
    echo "  🗄️  MySQL:        порт 3306"
    echo "  🗄️  PostgreSQL:   порт 5432"
    echo "  🗄️  MSSQL:        порт 1433"
    echo "  ❓ Unknown:       порты 8080, 8443"
    echo
    
    echo -e "${BLUE}🔧 Полезные команды:${NC}"
    echo "  Статус:           ./monitor_tpot.sh"
    echo "  Логи:             docker-compose logs -f"
    echo "  Перезапуск:       docker-compose restart"
    echo "  Остановка:        docker-compose down"
    echo "  Экспорт данных:   ./export_logs.sh"
    echo
    
    echo -e "${BLUE}📝 Логи развертывания сохранены в: $LOG_FILE${NC}"
    echo
    
    echo -e "${YELLOW}⚠️  Важно:${NC}"
    echo "  • T-Pot автоматически запустится при перезагрузке системы"
    echo "  • Регулярно проверяйте логи на предмет реальных угроз"
    echo "  • Делайте резервные копии данных"
    echo "  • Обновляйте Docker образы: docker-compose pull"
    echo
}

# Главная функция
main() {
    echo -e "${BLUE}Начинаем развертывание T-Pot Honeypot...${NC}"
    echo
    
    check_os
    check_requirements
    install_dependencies
    configure_firewall
    create_project_structure
    create_config_files
    
    # Предупреждение о Docker правах
    if ! groups $USER | grep -q docker; then
        echo -e "${YELLOW}⚠️  Необходимо перелогиниться для применения прав Docker${NC}"
        read -p "Продолжить? Docker команды могут не работать. (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Перелогиньтесь и запустите скрипт снова."
            exit 0
        fi
    fi
    
    start_tpot
    verify_installation
    create_systemd_service
    create_monitoring_scripts
    show_results
    
    echo -e "${GREEN}🎉 Развертывание T-Pot завершено успешно!${NC}"
}

# Обработка прерывания
trap 'echo -e "\n${RED}❌ Развертывание прервано${NC}"; exit 1' INT TERM

# Запуск
main "$@"
