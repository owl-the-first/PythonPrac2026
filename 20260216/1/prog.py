import sys
from pathlib import Path


def list_branches(repo):
    heads = Path(repo) / ".git" / "refs" / "heads"
    for branch in sorted(heads.iterdir()):
        print(branch.name)


repo = sys.argv[1]
list_branches(repo)

