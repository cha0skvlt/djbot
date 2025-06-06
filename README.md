# DJ BOT @cha0skvlt

Простой Telegram-бот для музыкантов. Два плейлиста в SQLite, запуск в Docker.

## Возможности
- `NITRO⚡️PULSE` и `NITRO⚡️BEAT`
- отправка последних треков (если меньше трёх — всё что есть)
- непрерывный стрим треков в голосовом чате
- добавление треков через CLI

## Быстрый старт
```bash
cp bot/.env.example bot/.env # заполните токены и ID
docker-compose up --build
```

Добавить трек:
```bash
cd bot
python admin_tools.py --playlist pulse --file path/to/song.mp3 --title "Song"
```

MIT License

