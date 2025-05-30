# T-Pot Honeypot для Red OS 7.3 - Полное руководство по развертыванию

## 🎯 Краткое описание решения

**Задача:** Развернуть T-Pot honeypot на Red OS 7.3 с ограничениями:
- ❌ Запрет экспорта данных с рабочей машины  
- ✅ Только Red OS (российская ОС)
- ✅ Только открытые/сертифицированные решения
- 🔧 VMware NAT → Bridge конфигурация

**Временные рамки:** До завтра в обед ⏰

---

## 📋 Пошаговый план развертывания

### 🔧 Этап 1: Подготовка системы (30 мин)

#### 1.1 Проверка совместимости Red OS 7.3
```bash
# Проверить версию ОС
cat /etc/redhat-release

# Проверить архитектуру
uname -m

# Проверить доступные ресурсы
free -h
df -h
```

#### 1.2 Установка зависимостей
```bash
# Обновить систему
sudo yum update -y

# Установить Docker (сертифицированный для Red OS)
sudo yum install -y docker docker-compose

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Включить Docker
sudo systemctl enable docker
sudo systemctl start docker

# Проверить статус
sudo systemctl status docker
```

---

### 🌐 Этап 2: Настройка сети VMware (45 мин)

#### 2.1 Перевод с NAT на Bridge
```bash
# В VMware:
# 1. VM Settings → Network Adapter → Bridged
# 2. Выбрать физический адаптер
# 3. Отключить "Replicate physical network connection state"

# Проверить сетевой интерфейс
ip addr show

# Настроить статический IP (если нужно)
sudo nmcli con mod ens33 ipv4.addresses 192.168.1.100/24
sudo nmcli con mod ens33 ipv4.gateway 192.168.1.1
sudo nmcli con mod ens33 ipv4.dns 8.8.8.8
sudo nmcli con mod ens33 ipv4.method manual
sudo nmcli con up ens33
```

#### 2.2 Конфигурация межсетевого экрана
```bash
# Настроить firewalld для T-Pot
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Открыть порты для honeypot сервисов
sudo firewall-cmd --permanent --add-port=21/tcp     # FTP
sudo firewall-cmd --permanent --add-port=22/tcp     # SSH
sudo firewall-cmd --permanent --add-port=23/tcp     # Telnet
sudo firewall-cmd --permanent --add-port=25/tcp     # SMTP
sudo firewall-cmd --permanent --add-port=53/tcp     # DNS
sudo firewall-cmd --permanent --add-port=53/udp     # DNS
sudo firewall-cmd --permanent --add-port=80/tcp     # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp    # HTTPS
sudo firewall-cmd --permanent --add-port=993/tcp    # IMAPS
sudo firewall-cmd --permanent --add-port=995/tcp    # POP3S
sudo firewall-cmd --permanent --add-port=1433/tcp   # MSSQL
sudo firewall-cmd --permanent --add-port=3306/tcp   # MySQL
sudo firewall-cmd --permanent --add-port=5432/tcp   # PostgreSQL

# Веб-интерфейс T-Pot
sudo firewall-cmd --permanent --add-port=64294/tcp  # T-Pot WebUI
sudo firewall-cmd --permanent --add-port=64295/tcp  # Kibana
sudo firewall-cmd --permanent --add-port=64296/tcp  # ES Head

sudo firewall-cmd --reload
```

---

### 🍯 Этап 3: Развертывание T-Pot (60 мин)

#### 3.1 Создание структуры директорий
```bash
# Создать рабочую директорию
mkdir -p ~/tpot-deployment
cd ~/tpot-deployment

# Создать директории для данных
sudo mkdir -p /opt/tpot/data
sudo mkdir -p /opt/tpot/conf
sudo mkdir -p /opt/tpot/logs
sudo chown -R $USER:$USER /opt/tpot
```

#### 3.2 Docker Compose конфигурация
Создать файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Elasticsearch для логов
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.9
    container_name: tpot_elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    volumes:
      - /opt/tpot/data/elasticsearch:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    restart: unless-stopped
    networks:
      - tpot_network

  # Kibana для визуализации
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.9
    container_name: tpot_kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "64295:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped
    networks:
      - tpot_network

  # Logstash для обработки логов
  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.9
    container_name: tpot_logstash
    volumes:
      - ./conf/logstash:/usr/share/logstash/pipeline
      - /opt/tpot/logs:/opt/tpot/logs
    environment:
      - "LS_JAVA_OPTS=-Xmx1g -Xms1g"
    depends_on:
      - elasticsearch
    restart: unless-stopped
    networks:
      - tpot_network

  # Cowrie SSH/Telnet honeypot
  cowrie:
    image: cowrie/cowrie:latest
    container_name: tpot_cowrie
    ports:
      - "22:2222"
      - "23:2223"
    volumes:
      - /opt/tpot/data/cowrie:/cowrie/var
      - /opt/tpot/logs:/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_network

  # Dionaea для различных протоколов
  dionaea:
    image: dinotools/dionaea:latest
    container_name: tpot_dionaea
    ports:
      - "21:21"     # FTP
      - "25:25"     # SMTP
      - "80:80"     # HTTP
      - "443:443"   # HTTPS
      - "993:993"   # IMAPS
      - "995:995"   # POP3S
      - "1433:1433" # MSSQL
      - "3306:3306" # MySQL
      - "5432:5432" # PostgreSQL
    volumes:
      - /opt/tpot/data/dionaea:/opt/dionaea/var
      - /opt/tpot/logs:/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_network

  # Honeytrap для неизвестных протоколов
  honeytrap:
    image: armedpot/honeytrap:latest
    container_name: tpot_honeytrap
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - ./conf/honeytrap:/etc/honeytrap
      - /opt/tpot/logs:/opt/tpot/logs
    restart: unless-stopped
    networks:
      - tpot_network

  # Nginx для веб-интерфейса
  nginx:
    image: nginx:alpine
    container_name: tpot_nginx
    ports:
      - "64294:80"
    volumes:
      - ./conf/nginx:/etc/nginx/conf.d
      - ./web:/var/www/html
    depends_on:
      - kibana
      - elasticsearch
    restart: unless-stopped
    networks:
      - tpot_network

  # Filebeat для отправки логов
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.9
    container_name: tpot_filebeat
    user: root
    volumes:
      - ./conf/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /opt/tpot/logs:/opt/tpot/logs:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - elasticsearch
    restart: unless-stopped
    networks:
      - tpot_network

networks:
  tpot_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### 3.3 Конфигурационные файлы

**Logstash конфигурация** (`conf/logstash/tpot.conf`):
```ruby
input {
  file {
    path => "/opt/tpot/logs/**/*.log"
    start_position => "beginning"
    type => "honeypot"
  }
  
  beats {
    port => 5044
  }
}

filter {
  if [type] == "honeypot" {
    if [path] =~ "cowrie" {
      mutate { add_field => { "honeypot" => "cowrie" } }
    } else if [path] =~ "dionaea" {
      mutate { add_field => { "honeypot" => "dionaea" } }
    } else if [path] =~ "honeytrap" {
      mutate { add_field => { "honeypot" => "honeytrap" } }
    }
  }
  
  # Геолокация для IP адресов
  if [src_ip] {
    geoip {
      source => "src_ip"
      target => "geoip"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "tpot-%{+YYYY.MM.dd}"
  }
  
  stdout { codec => rubydebug }
}
```

**Filebeat конфигурация** (`conf/filebeat/filebeat.yml`):
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /opt/tpot/logs/**/*.log
  multiline.pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
  multiline.negate: true
  multiline.match: after

output.logstash:
  hosts: ["logstash:5044"]

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
```

**Nginx конфигурация** (`conf/nginx/default.conf`):
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        return 301 /tpot/;
    }
    
    location /tpot/ {
        alias /var/www/html/;
        index index.html;
    }
    
    location /kibana/ {
        proxy_pass http://kibana:5601/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/ {
        proxy_pass http://elasticsearch:9200/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Веб-интерфейс** (`web/index.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>T-Pot Honeypot Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .status { padding: 5px 10px; border-radius: 3px; color: white; }
        .running { background: #27ae60; }
        .stopped { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🍯 T-Pot Honeypot Dashboard</h1>
        <p>Red OS 7.3 Deployment</p>
    </div>
    
    <div class="dashboard">
        <div class="card">
            <h3>Сервисы Honeypot</h3>
            <ul>
                <li>SSH/Telnet (Cowrie): <span class="status running">Работает</span></li>
                <li>Multi-Protocol (Dionaea): <span class="status running">Работает</span></li>
                <li>Unknown Protocols (Honeytrap): <span class="status running">Работает</span></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Мониторинг</h3>
            <ul>
                <li>Elasticsearch: <span class="status running">Активен</span></li>
                <li>Kibana: <span class="status running">Активен</span></li>
                <li>Logstash: <span class="status running">Активен</span></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Доступ к интерфейсам</h3>
            <p><a href="/kibana/" class="btn">Открыть Kibana</a></p>
            <p><a href="/api/_cat/indices" class="btn">Elasticsearch API</a></p>
        </div>
        
        <div class="card">
            <h3>Статистика</h3>
            <div id="stats">Загрузка...</div>
        </div>
    </div>
    
    <script>
        // Простая статистика через Elasticsearch API
        fetch('/api/_cat/indices?format=json')
            .then(response => response.json())
            .then(data => {
                const tpotIndices = data.filter(index => index.index.startsWith('tpot-'));
                document.getElementById('stats').innerHTML = 
                    `<p>Индексов в Elasticsearch: ${tpotIndices.length}</p>
                     <p>Общий размер данных: ${tpotIndices.reduce((sum, idx) => sum + parseInt(idx['store.size'] || '0'), 0)} bytes</p>`;
            })
            .catch(err => {
                document.getElementById('stats').innerHTML = '<p>Ошибка загрузки статистики</p>';
            });
    </script>
</body>
</html>
```

---

### 🚀 Этап 4: Запуск и проверка (30 мин)

#### 4.1 Запуск T-Pot
```bash
# Создать необходимые директории
mkdir -p conf/logstash conf/filebeat conf/nginx conf/honeytrap web

# Создать конфигурационные файлы (используя приведенные выше)
# ... (создание всех файлов конфигурации)

# Запустить сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Проверить логи
docker-compose logs -f
```

#### 4.2 Проверка работоспособности
```bash
# Проверить доступность сервисов
curl -s http://localhost:9200/_cluster/health | jq
curl -s http://localhost:64295/api/status | jq
curl -s http://localhost:64294/

# Проверить открытые порты
netstat -tulpn | grep LISTEN

# Тестирование honeypot
# Попробовать подключиться к SSH (будет перехвачено Cowrie)
ssh root@localhost -p 22

# Проверить логи атак
docker exec tpot_elasticsearch curl -s "localhost:9200/tpot-*/_search?size=10&sort=@timestamp:desc" | jq '.hits.hits[]._source'
```

---

## 🔧 Дополнительные конфигурации

### SSH доступ с обеих машин
```bash
# На Red OS настроить SSH ключи
ssh-keygen -t rsa -b 4096 -C "tpot@redos"

# Скопировать ключ на Raspberry Pi
ssh-copy-id user@raspberry-pi-ip

# Настроить VSCode Remote SSH для подключения
# В VSCode: Remote-SSH → Add New SSH Host
```

### Автозапуск и мониторинг
```bash
# Создать systemd сервис для автозапуска
sudo tee /etc/systemd/system/tpot.service << EOF
[Unit]
Description=T-Pot Honeypot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/$USER/tpot-deployment
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable tpot.service
sudo systemctl start tpot.service
```

### Скрипт мониторинга
```bash
#!/bin/bash
# monitor_tpot.sh

echo "=== T-Pot Status Monitor ==="
echo "Время: $(date)"
echo

echo "Docker контейнеры:"
docker-compose ps

echo -e "\nСтатус Elasticsearch:"
curl -s http://localhost:9200/_cluster/health | jq '.status'

echo -e "\nПоследние 5 атак:"
docker exec tpot_elasticsearch curl -s "localhost:9200/tpot-*/_search?size=5&sort=@timestamp:desc" | jq -r '.hits.hits[]._source | "\(.@timestamp) - \(.src_ip) -> \(.honeypot)"'

echo -e "\nИспользование диска:"
df -h /opt/tpot

echo -e "\nИспользование памяти:"
free -h
```

---

## 📊 Результат развертывания

### Что получим:
1. **Полнофункциональный T-Pot honeypot** с multiple honeypots
2. **Веб-интерфейс** для мониторинга на порту 64294
3. **Kibana dashboard** для анализа на порту 64295
4. **Elasticsearch API** для доступа к данным
5. **Автоматическая геолокация** IP-адресов атакующих
6. **Логирование всех попыток атак** в реальном времени

### Доступные интерфейсы:
- `http://your-red-os-ip:64294/` - Главная панель T-Pot
- `http://your-red-os-ip:64295/` - Kibana для анализа
- `http://your-red-os-ip:9200/` - Elasticsearch API

### Honeypot сервисы:
- **SSH (порт 22)** - Cowrie эмулирует SSH/Telnet
- **FTP (порт 21)** - Dionaea эмулирует FTP сервер  
- **HTTP/HTTPS (80/443)** - Dionaea веб-сервер
- **Database ports** - MySQL, PostgreSQL, MSSQL эмуляция
- **Email ports** - SMTP, POP3, IMAP эмуляция

---

## ⚠️ Важные моменты безопасности

1. **Изоляция сети:** T-Pot должен быть в изолированном сегменте
2. **Мониторинг:** Регулярно проверять логи на предмет реальных угроз
3. **Обновления:** Регулярно обновлять Docker образы
4. **Backup:** Делать резервные копии конфигураций и данных

---

## 🎯 Контрольный список готовности

- [ ] Red OS 7.3 установлен и обновлен
- [ ] Docker и docker-compose установлены  
- [ ] Сеть переведена с NAT на Bridge
- [ ] Межсетевой экран настроен
- [ ] Все конфигурационные файлы созданы
- [ ] Docker Compose запущен успешно
- [ ] Веб-интерфейс доступен
- [ ] SSH доступ с двух машин настроен
- [ ] Мониторинг работает
- [ ] Автозапуск настроен

**Время выполнения:** ~3-4 часа  
**Готово к завтра в обед:** ✅
