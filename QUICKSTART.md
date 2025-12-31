# Быстрое развертывание SimpleVote

## Одной командой (для опытных пользователей)

```bash
# На сервере выполните:
cd /tmp && \
sudo mkdir -p /srv/simplevote && \
sudo chown $USER:$USER /srv/simplevote && \
cd /srv/simplevote && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install fastapi uvicorn[standard] pydantic && \
sudo cp simplevote.service /etc/systemd/system/ && \
sudo cp simplevote.conf /etc/nginx/sites-available/ && \
sudo ln -s /etc/nginx/sites-available/simplevote.conf /etc/nginx/sites-enabled/ && \
sudo systemctl daemon-reload && \
sudo systemctl start simplevote && \
sudo systemctl enable simplevote && \
sudo nginx -t && \
sudo systemctl restart nginx
```

## Пошагово

### 1. Установка зависимостей
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
```

### 2. Развертывание приложения
```bash
sudo mkdir -p /srv/simplevote
sudo chown $USER:$USER /srv/simplevote
cd /srv/simplevote

# Скопируйте файлы проекта сюда

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка сервиса
```bash
sudo cp simplevote.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start simplevote
sudo systemctl enable simplevote
```

### 4. Настройка Nginx
```bash
sudo cp simplevote.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/simplevote.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Настройка DNS
Добавьте A-запись: `vote.llmtech.ru` → IP вашего сервера

### 6. HTTPS (рекомендуется)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d vote.llmtech.ru
```

## Проверка

- Главная: http://vote.llmtech.ru/
- Админка: http://vote.llmtech.ru/admin.html
- API docs: http://vote.llmtech.ru/api/docs

## Управление

```bash
# Логи
sudo journalctl -u simplevote -f

# Перезапуск
sudo systemctl restart simplevote
```

Подробная инструкция: см. [DEPLOY.md](DEPLOY.md)
