import concurrent.futures
import logging
import os
import pytesseract
import yaml
from localchecker import LocalChecker
from remotechecker import RemoteChecker
from reroll import Reroll

DEAFULT_SCREENSHOT_DIR = "screenshot"
DEFAUlT_BACKUP_DIR = "backup"
DEFAUlT_LOG_DIR = "log"
DEFAUlT_DATA_DIR = "data"

os.makedirs(DEAFULT_SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DEFAUlT_BACKUP_DIR, exist_ok=True)
os.makedirs(DEFAUlT_LOG_DIR, exist_ok=True)
os.makedirs(DEFAUlT_DATA_DIR, exist_ok=True)

# Load configuration from settings.yaml
with open("settings.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

debug_mode = config.get("debug", False)
reroll_config = config.get("reroll", {})
adb_ports = config.get("adb_ports", [])
pack_checker_config = config.get("pack_checker", {})
use_pack_checker = pack_checker_config.get("use_remote_checker", False)
checker = (
    RemoteChecker(
        pack_checker_config.get("url"),
        pack_checker_config.get("username"),
        pack_checker_config.get("password"),
    )
    if use_pack_checker
    else LocalChecker(f"{DEFAUlT_DATA_DIR}/data.db")
)
tesseract_path = config.get("tesseract_path", None)
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

logging.basicConfig(
    level=logging.WARNING if not debug_mode else logging.INFO,
    format="%(asctime)s - [%(levelname)s] [%(threadName)s] %(message)s",
    filename=f"{DEFAUlT_LOG_DIR}/reroll.log",
    filemode="a",
)


def start_reroll(adb_port):
    reroll_instance = Reroll(
        adb_port,
        reroll_pack=reroll_config.get("pack", None),
        checker=checker,
        debug_mode=debug_mode,
        delay_ms=reroll_config.get("delay_ms"),
        game_speed=reroll_config.get("game_speed"),
        swipe_speed=reroll_config.get("swipe_speed"),
        confidence=reroll_config.get("confidence"),
        timeout=reroll_config.get("timeout"),
        language=reroll_config.get("language"),
        account_name=reroll_config.get("account_name"),
        max_packs_to_open=reroll_config.get("max_packs_to_open"),
    )
    reroll_instance.start()


if __name__ == "__main__":
    max_workers = config.get("max_workers", None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(start_reroll, adb_ports)
