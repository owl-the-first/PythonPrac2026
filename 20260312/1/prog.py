import cmd
import shlex
from io import StringIO
from cowsay import cowsay, list_cows, read_dot_cow

FIELD_SIZE = 10
WEAPONS = {
    "sword": 10,
    "spear": 15,
    "axe": 20,
}
player_x = 0
player_y = 0
monsters = {}
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


def encounter(x, y):
    if (x, y) in monsters:
        name, hello, hp = monsters[(x, y)]
        show_monster(name, hello)


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
    if not is_known_monster(name):
        print("Cannot add unknown monster")
        return
    replaced = (x, y) in monsters
    monsters[(x, y)] = (name, hello, hp)
    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
    if replaced:
        print("Replaced the old monster")


def attack_current_monster(damage):
    if (player_x, player_y) not in monsters:
        print("No monster here")
        return
    name, hello, hp = monsters[(player_x, player_y)]
    real_damage = min(damage, hp)
    hp -= real_damage
    print(f"Attacked {name}, damage {real_damage} hp")
    if hp == 0:
        print(f"{name} died")
        del monsters[(player_x, player_y)]
    else:
        monsters[(player_x, player_y)] = (name, hello, hp)
        print(f"{name} now has {hp}")


class MudShell(cmd.Cmd):
    prompt = ""

    def do_up(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            move(0, -1)

    def do_down(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            move(0, 1)

    def do_left(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            move(-1, 0)

    def do_right(self, arg):
        if arg:
            print("Invalid arguments")
        else:
            move(1, 0)

    def do_addmon(self, arg):
        args = shlex.split(arg)
        if (
            len(args) == 8
            and args[1] == "hello"
            and args[3] == "hp"
            and args[5] == "coords"
        ):
            try:
                addmon(args)
            except ValueError:
                print("Invalid arguments")
        else:
            print("Invalid arguments")

    def do_attack(self, arg):
        args = shlex.split(arg)
        if len(args) == 0:
            attack_current_monster(WEAPONS["sword"])
        elif len(args) == 2 and args[0] == "with" and args[1] in WEAPONS:
            attack_current_monster(WEAPONS[args[1]])
        elif len(args) == 2 and args[0] == "with":
            print("Unknown weapon")
        else:
            print("Invalid arguments")
            
    def complete_attack(self, text, line, begidx, endidx):
        words = shlex.split(line[:begidx])
        if words == ["attack"]:
            variants = ["with"]
        elif words == ["attack", "with"]:
            variants = list(WEAPONS)
        else:
            variants = []
        return [variant for variant in variants if variant.startswith(text)]

    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


print("<<< Welcome to Python-MUD 0.1 >>>")
MudShell().cmdloop()
