import random
import shlex
import socket
import threading
import time

HOST = "localhost"
PORT = 1337
FIELD_SIZE = 10
MONSTER_MOVE_DELAY = 30
players = {}
clients = {}
monsters = {}
locales = {}
monsters_can_move = True
lock = threading.Lock()


def send(conn, message):
    conn.sendall((message + "\n").encode())


def broadcast(message):
    for conn in list(clients.values()):
        send(conn, message)


def move(username, dx, dy):
    x, y = players[username]
    x = (x + dx) % FIELD_SIZE
    y = (y + dy) % FIELD_SIZE
    players[username] = (x, y)
    answer = [f"Moved to ({x}, {y})"]
    if (x, y) in monsters:
        name, hello, hp = monsters[(x, y)]
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


def sayall(username, args):
    message = args[0]
    broadcast(f"{username}: {message}")
    return ""


def movemonsters(args):
    global monsters_can_move
    if len(args) != 1 or args[0] not in ("on", "off"):
        return "Invalid arguments"
    monsters_can_move = args[0] == "on"
    return f"Moving monsters: {args[0]}"
    

def set_locale(username, args):
    if len(args) != 1:
        return "Invalid arguments"
    locales[username] = args[0]
    return f"Set up locale: {args[0]}"
    
    
def handle_command(username, line):
    parts = shlex.split(line)
    command = parts[0]
    args = parts[1:]
    if command == "move":
        return move(username, int(args[0]), int(args[1]))
    if command == "addmon":
        answer = addmon(args)
        broadcast(f"{username}: {answer}")
        return answer
    if command == "attack":
        answer = attack(args)
        broadcast(f"{username}: {answer}")
        return answer
    if command == "sayall":
        return sayall(username, args)
    if command == "movemonsters":
        return movemonsters(args)
    if command == "locale":
        return set_locale(username, args)
    return "Invalid command"


def monster_direction():
    return random.choice([
        ("up", 0, -1),
        ("down", 0, 1),
        ("left", -1, 0),
        ("right", 1, 0),
    ])


def players_at(x, y):
    result = []
    for username, coords in players.items():
        if coords == (x, y):
            result.append(clients[username])
    return result


def move_random_monster():
    if not monsters:
        return
    old_coords = random.choice(list(monsters))
    name, hello, hp = monsters[old_coords]
    direction, dx, dy = monster_direction()
    old_x, old_y = old_coords
    new_x = (old_x + dx) % FIELD_SIZE
    new_y = (old_y + dy) % FIELD_SIZE
    new_coords = (new_x, new_y)
    if new_coords in monsters:
        return
    del monsters[old_coords]
    monsters[new_coords] = (name, hello, hp)
    broadcast(f"{name} moved one cell {direction}")
    for conn in players_at(new_x, new_y):
        send(conn, f"MONSTER {name} {hello}")


def move_monsters_periodically():
    while True:
        time.sleep(MONSTER_MOVE_DELAY)
        with lock:
            if monsters_can_move:
                move_random_monster()


def client_processing(conn, addr):
    username = conn.recv(4096).decode().strip()
    with lock:
        if username in clients:
            send(conn, "Username is already taken")
            conn.close()
            return
        clients[username] = conn
        players[username] = (0, 0)
        send(conn, f"Welcome, {username}")
        broadcast(f"{username} joined the game")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            request = data.decode().strip()
            with lock:
                response = handle_command(username, request)
            if response:
                send(conn, response)
    finally:
        with lock:
            if username in clients:
                del clients[username]
            if username in players:
                del players[username]
            if username in locales:
                del locales[username]
            broadcast(f"{username} left the game")
        conn.close()


def main():
    mover = threading.Thread(target=move_monsters_periodically)
    mover.daemon = True
    mover.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print("Server started")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=client_processing,
                args=(conn, addr),
            )
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    main()
