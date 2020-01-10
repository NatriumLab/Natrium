from pathlib import Path

def Delete(resourceHash):
    resourceFile = Path(f"./assets/resources/{resourceHash}.png")
    if resourceFile.exists():
        if resourceFile.is_file():
            resourceFile.unlink()