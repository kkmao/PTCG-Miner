import concurrent.futures
import logging
import os
import pytesseract
import time
import yaml
from adbutils import adb
from discordmsg import DiscordMsg
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
discord_config = config.get("discord", {})
discord_msg = DiscordMsg(
    webhook_url=discord_config.get("webhook_url"),
    user_id=discord_config.get("user_id"),
)
heatbeat_discord_msg = DiscordMsg(
    webhook_url=discord_config.get("heat_beat_url"),
    user_id=discord_config.get("user_id"),
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


def get_reroll_instance(adb_device):
    if adb_device.get_state() == "device":
        return Reroll(
            reroll_pack=reroll_config.get("pack", None),
            adb_device=adb_device,
            friend_code_seeker=friend_seeker,
            discord_msg=discord_msg,
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
    else:
        logging.warning(f"Device {adb_device.serial} is not connected")


if __name__ == "__main__":
    for adb_port in adb_ports:
        adb.connect(f"127.0.0.1:{adb_port}")
    max_workers = config.get("max_workers", None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务到线程池
        reroll_workers = []
        for device in adb.device_list():
            reroll_workers.append(get_reroll_instance(device))

        reroll_futures = {
            executor.submit(worker.start): worker for worker in reroll_workers
        }

        start_time = time.time()
        # 检查所有 worker 的状态
        while reroll_futures:
            total_pack_opened = 0
            running_time = (time.time() - start_time) / 60
            online_workers = []
            for future in list(reroll_futures.keys()):
                if future.running():
                    worker = reroll_futures[future]
                    worker_status = worker.status()
                    total_pack_opened += worker_status["total_pack"]
                    online_workers.append(worker_status["port"])
                elif future.done() or future.cancelled() or future.exception():
                    reroll_futures.pop(future)
            offline_workers = list(set(adb_ports) - set(online_workers))
            heatbeat_message = (
                f"{reroll_config.get("account_name")}\n"
                + f"Online: {", ".join(online_workers) if online_workers else 'none'}.\n"
                + f"Offline: {", ".join(offline_workers) if offline_workers else 'none'}.\n"
                + f"Time: {running_time:.0f}m Packs: {total_pack_opened}\n"
            )
            heatbeat_discord_msg.send_message(heatbeat_message)
            if not reroll_futures:
                print("All workers are done")
                break
            time.sleep(1800)
