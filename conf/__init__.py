import yaml
from pathlib import Path

config = yaml.safe_load(open(f"{Path.cwd()}/config.yaml"))