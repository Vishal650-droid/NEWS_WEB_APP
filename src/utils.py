
import os
import json
import logging
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
   
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  [%(levelname)s]  %(name)s  →  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(name)


def ensure_dir(path: str) -> None:
    
    os.makedirs(path, exist_ok=True)


# def save_json(data: list | dict, filepath: str) -> None:
from typing import Union

def save_json(data: Union[list, dict], filepath: str) -> None:
    
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# def load_json(filepath: str) -> list | dict:
from typing import Union

def load_json(filepath: str) -> Union[list, dict]:
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def timestamp_filename(prefix: str, ext: str = "csv") -> str:
    
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{ts}.{ext}"
