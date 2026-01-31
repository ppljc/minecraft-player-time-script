import json  # для чтения файлов игроков
import os  # для списка директорий
import argparse  # для аргументов при запуске

from pathlib import Path

dividers = {  # делители для выбранного режима
    "days": 20 * 60 * 60 * 24,  # тики в секунду * секунды в минуте * минуты в часе * часы в дне
    "hours": 20 * 60 * 60,
    "minutes": 20 * 60,
    "seconds": 20,
    "average": 20,  # будет считаться в секундах
    "full": 20  # так же в секундах
}

def prepare_usercache_file(usercache_file_path: Path):
    uuid_user_dict = {}

    with open(usercache_file_path, "r", encoding="utf-8") as usercache_file:
        usercache_file_json = json.load(usercache_file)

        usercache_file_json_len = len(usercache_file_json)

        for entry in usercache_file_json:
            uuid = entry.get("uuid")
            name = entry.get("name")
            if uuid and name:
                uuid_user_dict[uuid] = name

    return uuid_user_dict, usercache_file_json_len


def is_usercache_valid(usercache_file_path: Path):
    try:
        with open(usercache_file_path, "r", encoding="utf-8") as usercache_file:
            json.load(usercache_file)
        return True
    except json.decoder.JSONDecodeError:
        print("ERROR: Usercache file is not valid json")
        return False


def format_play_time(seconds: int):
    days, seconds = divmod(seconds, 60 * 60 * 24)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)

    output_string = ""

    if days:
        output_string += f"{int(days)} days "
    if hours:
        output_string += f"{int(hours)} hours "
    if minutes:
        output_string += f"{int(minutes)} minutes "

    output_string += f"{round(seconds)} seconds"

    return output_string


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-pd", "--playersDirectory", type=str, help="Directory with players files", required=True)

    parser.add_argument("-f", "--format", type=str, help="Calculation format: full, days, hours, minutes, seconds, average", choices=["full", "days", "hours", "minutes", "seconds", "average"], default="full")

    parser.add_argument("-o", "--outputFile", type=str, help="File for output", required=True)

    parser.add_argument("-uc", "--usercache", type=str, help="Usercache file for usernames match", required=True)

    parser.add_argument("-sa", "--serverAge", type=int, help="Server age in days", required=False)

    args = parser.parse_args()

    players_directory_path = Path(args.playersDirectory).resolve()
    calculation_format = args.format
    output_file_path = Path(args.outputFile).resolve()
    usercache_file_path = Path(args.usercache).resolve()
    server_age = args.serverAge

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

    if not is_usercache_valid(usercache_file_path):
        print("ERROR: Usercache file is not valid")
        return

    if not isinstance(calculation_format, str):
        print("ERROR: Format is not a string")
        return

    if server_age and not isinstance(server_age, int):
        print("ERROR: Server age is not an integer")
        return

    print("DEBUG: Preparing usercache file")
    uuid_user_dict, usercache_list_len = prepare_usercache_file(usercache_file_path)
    if len(uuid_user_dict) == usercache_list_len:
        print("DEBUG: Usercache file prepared successfully")
    else:
        print("ERROR: Usercache file preparetion failed")
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

                username = uuid_user_dict[uuid]
                user_stats = player_file_read_json.get("stats")
                user_stats_custom = user_stats.get("minecraft:custom")
                play_time = user_stats_custom.get("minecraft:play_time") / dividers[calculation_format]

                output_string = f"PLAYER: {username}\n"

                if calculation_format == "full":
                    play_time_formatted = format_play_time(play_time)
                    output_string += f"PLAY_TIME: {play_time_formatted}\n"
                elif calculation_format == "average":
                    pass
                else:
                    output_string += f"PLAY_TIME: {round(play_time, 2)} {calculation_format}\n"

                if server_age:
                    play_time_average = play_time / server_age
                    if calculation_format == "full" or calculation_format == "average":
                        play_time_average_formatted = format_play_time(play_time_average)
                        output_string += f"PLAT_TIME_AVERAGE: {play_time_average_formatted}\n"
                    else:
                        output_string += f"PLAY_TIME_AVERAGE: {round(play_time_average, 2)} {calculation_format}\n"

                output_string += "\n"

                players_stats[uuid] = { "play_time": play_time, "output_string": output_string }

                print(f"DEBUG: {players_stats[uuid]}")
        except PermissionError:
            print(f"ERROR: Dont have permission to read players {uuid} file")
            return
        except json.decoder.JSONDecodeError:
            print(f"ERROR: Players {uuid} file is not valid json")
            return

    players_stats = dict(sorted(players_stats.items(), key=lambda item: item[1]["play_time"], reverse=True))  # сортировка словаря по значению play_time от большего к меньшему

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        header_string = (
            f"SERVER AGE: {server_age} days\n"
            f"UNIQUE PLAYERS COUNT: {len(players_stats)}\n\n"
        )
        output_file.write(header_string)

        for key, value in players_stats.items():
            output_file.write(value["output_string"])


if __name__ == "__main__":
    main()
