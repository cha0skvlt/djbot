import argparse
from database import add_track

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Добавление трека в плейлист")
    parser.add_argument("--playlist", choices=["pulse", "beat"], required=True,
                        help="Имя плейлиста: pulse или beat")
    parser.add_argument("--file", required=True, help="Путь к файлу .mp3")
    parser.add_argument("--title", required=True, help="Название трека")
    args = parser.parse_args()
    add_track(args.playlist, args.file, args.title)
    print(f"Добавлен трек '{args.title}' в плейлист {args.playlist}")
