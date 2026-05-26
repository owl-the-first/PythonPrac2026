import sys
from pathlib import Path
import zlib


def list_branches(repo):
    heads = Path(repo) / ".git" / "refs" / "heads"
    for branch in sorted(heads.iterdir()):
        print(branch.name)
        

def read_object(repo, obj_hash):
    obj_path = Path(repo) / ".git" / "objects" / obj_hash[:2] / obj_hash[2:]
    data = zlib.decompress(obj_path.read_bytes())
    header, content = data.split(b"\x00", 1)
    return content


def get_branch_commit(repo, branch):
    branch_path = Path(repo) / ".git" / "refs" / "heads" / branch
    return branch_path.read_text().strip()


def get_tree_hash(repo, commit_hash):
    commit = read_object(repo, commit_hash).decode()
    for line in commit.splitlines():
        if line.startswith("tree "):
            return line.split()[1]


def print_tree(repo, tree_hash):
    tree = read_object(repo, tree_hash)
    i = 0
    while i < len(tree):
        space = tree.find(b" ", i)
        zero = tree.find(b"\x00", space)
        mode = tree[i:space].decode()
        name = tree[space + 1:zero].decode()
        obj_hash = tree[zero + 1:zero + 21].hex()
        print(mode, obj_hash, name)
        i = zero + 21
        
        
repo = sys.argv[1]
if len(sys.argv) == 2:
    list_branches(repo)
else:
    branch = sys.argv[2]
    commit_hash = get_branch_commit(repo, branch)
    tree_hash = get_tree_hash(repo, commit_hash)
    print_tree(repo, tree_hash)


