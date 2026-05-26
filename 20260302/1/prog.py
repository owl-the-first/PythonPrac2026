import shlex
from cowsay import cowsay, list_cows


FIELD_SIZE = 10

player_x = 0
player_y = 0
monsters = {}


def encounter(x, y):
    if (x, y) in monsters:
        name, hello, hp = monsters[(x, y)]
        print(cowsay(hello, cow=name), end="")


def move(dx, dy):
    global player_x, player_y
    player_x = (player_x + dx) % FIELD_SIZE
    player_y = (player_y + dy) % FIELD_SIZE
    print(f"Moved to ({player_x}, {player_y})")
    encounter(player_x, player_y)


def addmon(args):
    name = args[0]
    hello = args[2]
    hp = int(args[4])
    x = int(args[6])
    y = int(args[7])
    if name not in list_cows():
        print("Cannot add unknown monster")
        return
    replaced = (x, y) in monsters
    monsters[(x, y)] = (name, hello, hp)
    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
    if replaced:
        print("Replaced the old monster")


def handle_command(line):
    parts = shlex.split(line)
    if len(parts) == 0:
        return
    command = parts[0]
    args = parts[1:]
    if command == "up" and len(args) == 0:
        move(0, -1)
    elif command == "down" and len(args) == 0:
        move(0, 1)
    elif command == "left" and len(args) == 0:
        move(-1, 0)
    elif command == "right" and len(args) == 0:
        move(1, 0)
    elif (
        command == "addmon"
        and len(args) == 8
        and args[1] == "hello"
        and args[3] == "hp"
        and args[5] == "coords"
    ):
        try:
            addmon(args)
        except ValueError:
            print("Invalid arguments")
    elif command in ("up", "down", "left", "right", "addmon"):
        print("Invalid arguments")
    else:
        print("Invalid command")


while True:
    try:
        line = input()
        handle_command(line)
    except EOFError:
        break

