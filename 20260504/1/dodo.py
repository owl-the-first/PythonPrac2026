import shutil
from pathlib import Path

DOIT_CONFIG = {"default_tasks": ["html"]}

ROOT = Path(__file__).parent
MOOD = ROOT / "mood"
SERVER = MOOD / "server"
PO_DIR = SERVER / "po"
POT_FILE = PO_DIR / "mood.pot"
RU_PO = PO_DIR / "ru" / "LC_MESSAGES" / "mood.po"
RU_MO = PO_DIR / "ru" / "LC_MESSAGES" / "mood.mo"
DOC = ROOT / "doc"
HTML_DIR = DOC / "_build" / "html"
HTML_INDEX = HTML_DIR / "index.html"
PACKAGE_DOC = ROOT / "mood" / "doc_html"


def remove_file(path):
    if path.exists():
        path.unlink()


def clean_pot():
    remove_file(POT_FILE)


def clean_mo():
    remove_file(RU_MO)


def remove_html():
    if DOC.joinpath("_build").exists():
        shutil.rmtree(DOC / "_build")


def remove_package_doc():
    if PACKAGE_DOC.exists():
        shutil.rmtree(PACKAGE_DOC)


def copy_html_to_package():
    remove_package_doc()
    shutil.copytree(HTML_DIR, PACKAGE_DOC)


def task_pot():
    return {
        "actions": [
            f"pybabel extract -o {POT_FILE} {MOOD}",
        ],
        "file_dep": list(MOOD.rglob("*.py")),
        "targets": [POT_FILE],
        "clean": [clean_pot],
    }


def task_po():
    return {
        "actions": [
            f"pybabel update -i {POT_FILE} -d {PO_DIR} -D mood",
        ],
        "file_dep": [POT_FILE],
        "targets": [RU_PO],
    }


def task_mo():
    return {
        "actions": [
            f"pybabel compile -d {PO_DIR} -D mood",
        ],
        "file_dep": [RU_PO],
        "targets": [RU_MO],
        "clean": [clean_mo],
    }


def task_i18n():
    return {
        "actions": None,
        "task_dep": ["pot", "po", "mo"],
    }


def task_html():
    file_dep = list(DOC.glob("*.rst"))
    file_dep += list(DOC.glob("*.py"))
    file_dep += list(MOOD.rglob("*.py"))
    return {
        "actions": [
            f"sphinx-build -b html {DOC} {HTML_DIR}",
        ],
        "file_dep": file_dep,
        "targets": [HTML_INDEX],
        "clean": [remove_html],
    }


def task_test():
    file_dep = [ROOT / "test_server.py"]
    file_dep += list(MOOD.rglob("*.py"))
    return {
        "actions": [
            f"cd {ROOT} && python -m unittest test_server.py",
        ],
        "task_dep": ["i18n"],
        "file_dep": file_dep,
    }


def task_packagedoc():
    return {
        "actions": [copy_html_to_package],
        "task_dep": ["html"],
        "targets": [PACKAGE_DOC / "index.html"],
        "clean": [remove_package_doc],
    }


def task_wheel():
    return {
        "actions": [
            f"sphinx-build -b html {DOC} {HTML_DIR}",
            copy_html_to_package,
            f"pybabel compile -d {PO_DIR} -D mood",
            "python -m build --wheel",
        ],
    }
