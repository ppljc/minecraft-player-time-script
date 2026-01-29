import json  # для чтения файлов игроков
import os  # для списка директорий
import argparse  # для аргументов при запуске

from pathlib import Path

dividers = {  # делители для выбранного режима
    "hours": 20 * 60 * 60,
    "minutes": 20 * 60,
    "seconds": 20,
    "average": 20,  # будет считаться в секундах
    "full": 20  # так же в секундах
}

def get_name_by_uuid(uuid: str, usercache_file_path: Path):
    '''
    Получение имени игрока по UUID из файла кэша
    :param uuid: Minecraft UUID
    :param usercache_file_path: Path to usercache file
    :return: Minecraft username
    '''
    with open(usercache_file_path, "r", encoding="utf-8") as usercache_file:
        usercache_file_json = json.load(usercache_file)
        for entry in usercache_file_json:
            if entry["uuid"] == uuid:
                return entry["name"]
    return None

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-pd", "--playersDirectory", type=str, help="Directory with players files", required=True)

    parser.add_argument("-f", "--format", type=str, help="Calculation format: full, days, hours, minutes, seconds, average", choices=["full", "days", "hours", "minutes", "seconds", "average"], default="full")

    parser.add_argument("-o", "--outputFile", type=str, help="File for output", required=True)

    parser.add_argument("-uc", "--usercache", type=str, help="Usercache file for usernames match", required=True)

    args = parser.parse_args()

    players_directory_path = Path(args.playersDirectory).resolve()
    output_file_path = Path(args.outputFile).resolve()
    usercache_file_path = Path(args.usercache).resolve()

    print(f"DEBUG: {players_directory_path}")
    print(f"DEBUG: {output_file_path}")
    print(f"DEBUG: {usercache_file_path}")

    if not players_directory_path.exists():  # проверка на существование указанного пути
        print("ERROR: Players directory does not exist")
        return

    if not players_directory_path.is_dir():  # проверка на то, что указанный путь - директория
        print("ERROR: Players directory is not a directory")
        return

    if len(os.listdir(players_directory_path)) == 0:  # проверка на наличие файлов по указанному пути
        print("ERROR: Players directory is empty")
        return

    if not output_file_path.exists():  # проверка на существование указанного пути
        print("ERROR: Output file does not exist, will be created")
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write("")
        except PermissionError:
            print("ERROR: Dont have permission to create output file")
            return
        except FileNotFoundError:
            print("ERROR: Output file directory does not exist")
            return

    if not output_file_path.is_file():  # проверка на то, что указанный путь - файл
        print("ERROR: Output file is not a file")
        return

    if output_file_path.stat().st_size > 0:  # проверка на пустоту выходного файла
        print("ERROR: Output file is not empty")
        return

    if not usercache_file_path.exists():
        print("ERROR: Usercache file does not exist")
        return

    if not usercache_file_path.is_file():
        print("ERROR: Usercache file is not a file")
        return

    if usercache_file_path.stat().st_size == 0:
        print("ERROR: Usercache file is empty")
        return

    players_files = os.listdir(players_directory_path)

    players_stats = {}

    for player_file in players_files:
        uuid = player_file.removesuffix(".json")
        player_file_path = Path(players_directory_path, player_file)
        print(f"DEBUG: {player_file_path}")
        try:
            with open(player_file_path, "r", encoding="utf-8") as player_file_read:
                player_file_read_json = json.load(player_file_read)

                username = get_name_by_uuid(uuid, usercache_file_path)
                play_time = player_file_read_json['stats']['minecraft:custom']['minecraft:play_time'] / dividers[args.format]

                players_stats[username] = { "play_time": round(play_time, 2), "avg": play_time / 34 }

                print(f"DEBUG: username = {username}, hours = {int(player_file_read_json['stats']['minecraft:custom']['minecraft:play_time']) / (20 * 60 * 60)}")
        except PermissionError:
            print("ERROR: Dont have permission to read players files")
            return

    players_stats = dict(sorted(players_stats.items(), key=lambda item: item[1]["play_time"], reverse=True))

    for key, value in players_stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
