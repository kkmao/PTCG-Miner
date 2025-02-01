import concurrent.futures
import logging
import os
import pytesseract
import yaml
from adbutils import adb
from friendseeker import FriendSeeker
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
friends_config = config.get("friend_codes", [])
remote_friend_config = friends_config.get("remote_friend_codes", {})
local_friend_config = friends_config.get("local_friend_codes", {})
friend_seeker = FriendSeeker(
    url=remote_friend_config.get("url"),
    username=remote_friend_config.get("username"),
    password=remote_friend_config.get("password"),
    local_path=local_friend_config.get("path"),
    remote=friends_config.get("use_remote"),
    local=friends_config.get("use_local"),
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


def start_reroll(adb_device):
    if adb_device.get_state() == "device":
        reroll_instance = Reroll(
            reroll_pack=reroll_config.get("pack", None),
            adb_device=adb_device,
            friend_code_seeker=friend_seeker,
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
    else:
        logging.warning(f"Device {adb_device.serial} is not connected")


if __name__ == "__main__":
    for adb_port in adb_ports:
        adb.connect(f"127.0.0.1:{adb_port}")
    max_workers = config.get("max_workers", None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(start_reroll, adb.device_list())
