import cmd
import shlex
import socket
from io import StringIO
from cowsay import cowsay, list_cows, read_dot_cow

HOST = "localhost"
PORT = 1337
WEAPONS = {
    "sword": 10,
    "spear": 15,
    "axe": 20,
}
ABCDEFGH_COW = read_dot_cow(StringIO(r"""
$the_cow = <<EOC;
        $thoughts
         $thoughts
          /\_/\\
         ( o.o )
          > ^ <
        /       \\
       /  |   |  \\
      (_(_|___|_)_)
EOC
"""))


def is_known_monster(name):
    return name in list_cows() or name == "abcdefgh"


def show_monster(name, hello):
    if name == "abcdefgh":
        print(cowsay(hello, cowfile=ABCDEFGH_COW), end="")
    else:
        print(cowsay(hello, cow=name), end="")


def send_command(sock, command):
    sock.sendall((command + "\n").encode())
    return sock.recv(4096).decode().strip()


def print_response(response):
    for line in response.splitlines():
        if line.startswith("MONSTER "):
            parts = line.split(maxsplit=2)
            show_monster(parts[1], parts[2])
        else:
            print(line)


class MudClient(cmd.Cmd):
    prompt = ""

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def do_up(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            print_response(send_command(self.sock, "move 0 -1"))

    def do_down(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            print_response(send_command(self.sock, "move 0 1"))

    def do_left(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            print_response(send_command(self.sock, "move -1 0"))

    def do_right(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            print_response(send_command(self.sock, "move 1 0"))

    def do_addmon(self, arg):
        args = shlex.split(arg)
        if (
            len(args) == 8
            and args[1] == "hello"
            and args[3] == "hp"
            and args[5] == "coords"
        ):
            name = args[0]
            hello = args[2]
            hp = args[4]
            x = args[6]
            y = args[7]
            if not is_known_monster(name):
                print("Cannot add unknown monster")
                return
            request = f"addmon {shlex.quote(name)} {shlex.quote(hello)} {hp} {x} {y}"
            print_response(send_command(self.sock, request))
        else:
            print("Invalid arguments")

    def do_attack(self, arg):
        args = shlex.split(arg)
        if len(args) == 1:
            request = f"attack {args[0]} sword {WEAPONS['sword']}"
            print_response(send_command(self.sock, request))
        elif len(args) == 3 and args[1] == "with" and args[2] in WEAPONS:
            request = f"attack {args[0]} {args[2]} {WEAPONS[args[2]]}"
            print_response(send_command(self.sock, request))
        elif len(args) == 3 and args[1] == "with":
            print("Unknown weapon")
        else:
            print("Invalid arguments")

    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


print("<<< Welcome to Python-MUD 0.1 >>>")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    MudClient(sock).cmdloop()

