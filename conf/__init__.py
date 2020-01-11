import yaml
from pathlib import Path
import i18n

config = yaml.safe_load(open(f"{Path.cwd()}/config.yaml", encoding="utf-8"))

def update():
    config.update(yaml.safe_load(open(f"{Path.cwd()}/config.yaml", encoding="utf-8")))

i18n.load_path.append(str(Path("./assets/i18n/").resolve()))
i18n.set("locale", config['language'])
i18n.set("fallback", "zh_cn")