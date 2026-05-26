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


repo = sys.argv[1]
if len(sys.argv) == 2:
    list_branches(repo)
else:
    branch = sys.argv[2]
    commit_hash = get_branch_commit(repo, branch)
    print(read_object(repo, commit_hash).decode())

