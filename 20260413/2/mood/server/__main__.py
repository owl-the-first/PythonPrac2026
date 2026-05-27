import random
import shlex
import socket
import threading
import time
import gettext
from pathlib import Path

TEXT_DOMAIN = "mood"
LOCALE_DIR = Path(__file__).parent / "po"
DEFAULT_LOCALE = "en"
RU_LOCALE = "ru_RU.UTF8"
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


def send_event(recipient, message, **kwargs):
    text = _(recipient, message).format(**kwargs)
    send(clients[recipient], text)


def send_hp_event(recipient, singular, plural, number, **kwargs):
    text = ngettext(recipient, singular, plural, number).format(
        count=number,
        **kwargs,
    )
    send(clients[recipient], text)


def broadcast_event(message, **kwargs):
    for username in list(clients):
        send_event(username, message, **kwargs)


def broadcast_hp_event(singular, plural, number, **kwargs):
    for username in list(clients):
        send_hp_event(username, singular, plural, number, **kwargs)


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
    return name, hello, hp, x, y, replaced


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
        return None
    name, hello, hp = monsters[coords]
    real_damage = min(damage, hp)
    hp -= real_damage
    if hp == 0:
        del monsters[coords]
    else:
        monsters[coords] = (name, hello, hp)
    return name, weapon, real_damage, hp


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


def get_translation(username):
    locale_name = locales.get(username, DEFAULT_LOCALE)
    return gettext.translation(
        TEXT_DOMAIN,
        localedir=LOCALE_DIR,
        languages=[locale_name],
        fallback=True,
    )


def _(username, message):
    return get_translation(username).gettext(message)


def ngettext(username, singular, plural, number):
    return get_translation(username).ngettext(singular, plural, number)


def hp_text(username, number):
    return ngettext(
        username,
        "{count} health point",
        "{count} health points",
        number,
    ).format(count=number)


def set_locale(username, args):
    if len(args) != 1:
        return "Invalid arguments"
    locales[username] = args[0]
    return _(username, "Set up locale: {locale}").format(locale=args[0])


def translate_for(username, message, **kwargs):
    return _(username, message).format(**kwargs)


def handle_command(username, line):
    parts = shlex.split(line)
    command = parts[0]
    args = parts[1:]
    if command == "move":
        return move(username, int(args[0]), int(args[1]))
    if command == "addmon":
        name, hello, hp, x, y, replaced = addmon(args)
        broadcast_hp_event(
            "{username} added monster {name} to ({x}, {y}) with {count} hp",
            "{username} added monster {name} to ({x}, {y}) with {count} hp",
            hp,
            username=username,
            name=name,
            x=x,
            y=y,
        )
        if replaced:
            broadcast_event("Replaced the old monster")
        return ""
    if command == "attack":
        result = attack(args)
        if result is None:
            return translate_for(username, "No {name} here", name=args[0])
        name, weapon, damage, hp = result
        broadcast_hp_event(
            "{username} attacked {name} with {weapon}, damage {count} hp",
            "{username} attacked {name} with {weapon}, damage {count} hp",
            damage,
            username=username,
            name=name,
            weapon=weapon,
        )
        if hp == 0:
            broadcast_event("{name} died", name=name)
        else:
            broadcast_hp_event(
                "{name} now has {count} hp",
                "{name} now has {count} hp",
                hp,
                name=name,
            )
        return ""
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
    broadcast_event(
        "{name} moved one cell {direction}",
        name=name,
        direction=direction,
    )
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
        broadcast_event("{username} joined the game", username=username)
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
            broadcast_event("{username} left the game", username=username)
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
