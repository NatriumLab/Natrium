import yaml
from pathlib import Path

config = yaml.safe_load(open(f"{Path.cwd()}/config.yaml", encoding="utf-8"))

def update():
    config.update(yaml.safe_load(open(f"{Path.cwd()}/config.yaml", encoding="utf-8")))