# 🤖 Telegram AI-ассистент компании

Бот отвечает на вопросы о компании используя Claude AI и файл `company_info.txt` как базу знаний.

## Быстрый старт

### 1. Получите токены

**Telegram Bot Token:**
1. Откройте Telegram → найдите `@BotFather`
2. Напишите `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте полученный токен

**Anthropic API Key:**
1. Зайдите на [console.anthropic.com](https://console.anthropic.com)
2. Создайте аккаунт / войдите
3. Перейдите в API Keys → Create Key
4. Скопируйте ключ

### 2. Настройте окружение

```bash
# Клонируйте / скачайте файлы в папку
cd telegram-bot

# Создайте .env файл
cp .env.example .env

# Откройте .env и вставьте свои токены
nano .env   # или любой редактор
```

### 3. Заполните базу знаний

Откройте файл `company_info.txt` и замените шаблонные данные на реальную информацию о вашей компании.

Можно добавить любую информацию:
- Описание компании и услуг
- Адреса и контакты
- Цены и пакеты
- Вакансии
- FAQ

### 4. Установите зависимости и запустите

```bash
# Создайте виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Установите зависимости
pip install -r requirements.txt

# Запустите бота
python bot.py
```

## Структура проекта

```
telegram-bot/
├── bot.py              # Основной код бота
├── company_info.txt    # База знаний (заполните своими данными)
├── requirements.txt    # Python зависимости
├── .env.example        # Шаблон переменных окружения
├── .env                # Ваши токены (создать самостоятельно)
└── README.md           # Эта инструкция
```

## Как работает бот

1. Пользователь пишет вопрос в Telegram
2. Бот передаёт вопрос + информацию из `company_info.txt` в Claude API
3. Claude генерирует ответ на основе только этой информации
4. Бот отвечает пользователю

История диалога сохраняется в памяти (до 20 сообщений на пользователя), поэтому бот помнит контекст разговора.

## Запуск на сервере (Production)

```bash
# Через systemd (Linux)
sudo nano /etc/systemd/system/telegram-bot.service
```

```ini
[Unit]
Description=Telegram Company Bot
After=network.target

[Service]
WorkingDirectory=/path/to/telegram-bot
EnvironmentFile=/path/to/telegram-bot/.env
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```
