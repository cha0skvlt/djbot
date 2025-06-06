# Начало Prompt

Напиши полный проект Telegram-бота для музыкальной группы, разворачиваемого в Docker-контейнере. Бот должен быть написан на Python 3.11 и использовать библиотеку python-telegram-bot (или аналогичную, совместимую с Python 3.11). База данных должна быть SQLite: для каждого из двух плейлистов (NITRO⚡️PULSE и NITRO⚡️BEAT) используется свой отдельный файл базы данных (pulse.db и beat.db). Каждая база содержит таблицу tracks (id INTEGER PRIMARY KEY, file_path TEXT, title TEXT, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP). При запросе бот отсылает 3 последних по added_at трека из соответствующего файла.

Бот при старте (или при вызове команды) отправляет в указанный канал (CHAT_ID) сообщение с меню, содержащим две Inline-кнопки: "NITRO⚡️PULSE" и "NITRO⚡️BEAT". При нажатии пользователем любого из этих названий бот открывает личный чат с пользователем и отправляет ему три последние аудиозаписи из нужного плейлиста (через send_audio). Если треков меньше трёх или нет вообще, бот высылает сообщение "Треков пока нет" или "Недостаточно треков". Логику работы разделить по модулям: main.py, handlers.py, database.py, опционально admin_tools.py для добавления новых треков через CLI.

Перечень файлов и папок:
- project-root/
  - bot/
    - main.py                # запуск: чтение .env, инициализация бота, отправка меню в канал, регистрация хендлеров
    - handlers.py            # все обработчики: кнопки (callback_query), /start и т. д.
    - database.py            # функции init_databases(), add_track(), get_last_tracks()
    - admin_tools.py         # CLI-скрипт для добавления треков в pulse.db и beat.db
    - requirements.txt       # python-telegram-bot, python-dotenv
    - Dockerfile             # сборка контейнера с Python 3.11
    - .env.example           # пример .env с BOT_TOKEN и CHANNEL_CHAT_ID
  - docker-compose.yml
  - README.md

Файл bot/main.py должен:
- Загружать переменные из `bot/.env` (используя python-dotenv).
- Инициализировать Telegram-бота с BOT_TOKEN.
- В функции on_startup (или в блоке if __name__ == "__main__") вызывать `init_databases()` из database.py, а затем отправлять в канал сообщение с меню-кнопками (InlineKeyboardMarkup, callback_data = "pulse" и "beat").
- Регистрировать обработчики из handlers.py:
    - CallbackQueryHandler для нажатий на "pulse" или "beat"
    - (Опционально) CommandHandler("start") для приветствия

Файл bot/handlers.py должен содержать:
- Функцию `send_menu_to_channel(context)` — формирует InlineKeyboardMarkup с двумя кнопками (text="NITRO⚡️PULSE", callback_data="pulse" и text="NITRO⚡️BEAT", callback_data="beat") и отправляет его в чат с ID = CHANNEL_CHAT_ID.
- Функцию `button_callback_handler(update, context)`:
    1. Определяет `playlist_name = update.callback_query.data` ("pulse" или "beat").
    2. Вызывает `get_last_tracks(playlist_name, 3)` из database.py → получает список до трёх записей в формате `[{"file_path": ..., "title": ...}, ...]`.
    3. Если список пустой — отвечает пользователю `edit_message_text("Треков пока нет")`.
    4. Иначе перебирает записи и шлёт пользователю в личный чат `context.bot.send_audio(chat_id=update.effective_user.id, audio=open(file_path, 'rb'), title=title)`.
    5. После отправки треков можно отправить завершающее сообщение типа "Это последние три трека".

- (Опционально) Функцию `start_handler(update, context)`, которая выводит краткое приветствие и объясняет, как пользоваться ботом (например, "Нажмите кнопку в канале, чтобы получить треки").

Файл bot/database.py должен содержать:
```python
import sqlite3
import os

DB_MAPPING = {
    "pulse": "pulse.db",
    "beat": "beat.db"
}

def init_databases():
    for playlist, db_file in DB_MAPPING.items():
        if not os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute(
                '''
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
            conn.commit()
            conn.close()

def add_track(playlist_name: str, file_path: str, title: str):
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file:
        raise ValueError("Неправильное имя плейлиста")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        'INSERT INTO tracks (file_path, title) VALUES (?, ?)',
        (file_path, title)
    )
    conn.commit()
    conn.close()

def get_last_tracks(playlist_name: str, limit: int = 3):
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file or not os.path.exists(db_file):
        return []
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        'SELECT file_path, title FROM tracks ORDER BY added_at DESC LIMIT ?',
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"file_path": row[0], "title": row[1]} for row in rows]
Файл bot/admin_tools.py:

python
Копировать
Редактировать
import argparse
from database import add_track

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Добавление трека в плейлист")
    parser.add_argument("--playlist", choices=["pulse", "beat"], required=True, help="Имя плейлиста: pulse или beat")
    parser.add_argument("--file", required=True, help="Путь к файлу .mp3")
    parser.add_argument("--title", required=True, help="Название трека")
    args = parser.parse_args()
    add_track(args.playlist, args.file, args.title)
    print(f"Добавлен трек '{args.title}' в плейлист {args.playlist}")
Файл bot/requirements.txt:

shell
Копировать
Редактировать
python-telegram-bot>=20.0
python-dotenv
Файл bot/Dockerfile:

dockerfile
Копировать
Редактировать
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем .env
COPY .env .env

# Инициализация БД
RUN python - <<CODE
import database
database.init_databases()
CODE

CMD ["python", "main.py"]
Файл docker-compose.yml:

yaml
Копировать
Редактировать
version: "3.9"
services:
  telegram-bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    container_name: telegram_music_bot
    env_file:
      - ./bot/.env
    volumes:
      - ./bot/pulse.db:/app/pulse.db
      - ./bot/beat.db:/app/beat.db
      - ./music_files:/app/music_files
    restart: unless-stopped
Файл bot/.env.example:

ini
Копировать
Редактировать
BOT_TOKEN=ваш_токен_бота
CHANNEL_CHAT_ID=@имя_канала_или_числовой_ID
Файл README.md (в корне проекта):

markdown
Копировать
Редактировать
# Telegram-бот для музыкальной группы

## Описание
Этот бот позволяет участникам вашего Telegram-канала получать последние треки из двух плейлистов (NITRO⚡️PULSE и NITRO⚡️BEAT). При нажатии на кнопку в посте меню, бот отправляет в личный чат пользователя 3 последние аудиозаписи из соответствующего плейлиста.

## Требования
- Docker
- Docker Compose
- Python 3.11 (необязательно локально, всё работает в контейнере)

## Файловая структура
/project-root
├── bot/
│ ├── main.py
│ ├── handlers.py
│ ├── database.py
│ ├── admin_tools.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── .env.example
├── docker-compose.yml
└── README.md

markdown
Копировать
Редактировать

## Настройка и запуск
1. Скопируйте `bot/.env.example` в `bot/.env` и заполните:
BOT_TOKEN=ваш_токен_бота
CHANNEL_CHAT_ID=@имя_канала_или_числовой_ID

markdown
Копировать
Редактировать
2. Поместите аудиофайлы (.mp3) в папку `music_files/` (необязательно — можно добавлять через админ-скрипт).
3. Если нужно добавить треки вручную, выполните:
cd bot
python admin_tools.py --playlist pulse --file /path/to/track.mp3 --title "Название трека"
python admin_tools.py --playlist beat --file /path/to/track2.mp3 --title "Другое название"

markdown
Копировать
Редактировать
4. Из корневой папки проекта запустите:
docker-compose up --build

markdown
Копировать
Редактировать
5. После запуска бот автоматически отправит меню-сообщение в ваш канал. Пользователи нажимают кнопку → получают три последние аудиозаписи.

## Логика работы
- При старте контейнера вызывается `database.init_databases()`, создаются `pulse.db` и `beat.db`.
- В `main.py` формируется меню с двумя кнопками и отправляется в канал.
- Обработчик `button_callback_handler` получает callback_data ("pulse"/"beat"), запрашивает последние три записи, отправляет пользователю их через `send_audio`.

# Конец Prompt
Передавая этот текст (между тройными кавычками) в Codex, вы получите готовую файловую структуру и код для Telegram-бота, развёрнутого в Docker, с описанной логикой работы и подключением к SQLite-базам.
