import shlex
import socket

HOST = "localhost"
PORT = 1337
FIELD_SIZE = 10
player_x = 0
player_y = 0
monsters = {}


def move(dx, dy):
    global player_x, player_y
    player_x = (player_x + dx) % FIELD_SIZE
    player_y = (player_y + dy) % FIELD_SIZE
    answer = [f"Moved to ({player_x}, {player_y})"]
    if (player_x, player_y) in monsters:
        name, hello, hp = monsters[(player_x, player_y)]
        answer.append(f"MONSTER {name} {hello}")
    return "\n".join(answer)


def addmon(args):
    name = args[0]
    hello = args[1]
    hp = int(args[2])
    x = int(args[3])
    y = int(args[4])
    replaced = (x, y) in monsters
    monsters[(x, y)] = (name, hello, hp)
    answer = [f"Added monster {name} to ({x}, {y}) saying {hello}"]
    if replaced:
        answer.append("Replaced the old monster")
    return "\n".join(answer)


def find_monster_by_name(monster_name):
    for coords, monster in monsters.items():
        name, hello, hp = monster
        if name == monster_name:
            return coords
    return None


def attack(args):
    monster_name = args[0]
    weapon = args[1]
    damage = int(args[2])
    coords = find_monster_by_name(monster_name)
    if coords is None:
        return f"No {monster_name} here"
    name, hello, hp = monsters[coords]
    real_damage = min(damage, hp)
    hp -= real_damage
    answer = [f"Attacked {name} with {weapon}, damage {real_damage} hp"]
    if hp == 0:
        answer.append(f"{name} died")
        del monsters[coords]
    else:
        monsters[coords] = (name, hello, hp)
        answer.append(f"{name} now has {hp}")
    return "\n".join(answer)


def handle_command(line):
    parts = shlex.split(line)
    command = parts[0]
    args = parts[1:]
    if command == "move":
        return move(int(args[0]), int(args[1]))
    if command == "addmon":
        return addmon(args)
    if command == "attack":
        return attack(args)
    return "Invalid command"


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print("Server started")
    while True:
        conn, addr = server.accept()
        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                request = data.decode().strip()
                response = handle_command(request)
                conn.sendall((response + "\n").encode())


