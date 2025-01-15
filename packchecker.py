import requests
from requests.auth import HTTPBasicAuth
import logging

LOGGER = logging.getLogger("PackChecker")


class PackChecker:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def get_check_id(self):
        """
        获取待验证的ID
        """
        try:
            response = requests.get(
                self.url + "/get", auth=HTTPBasicAuth(self.username, self.password)
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            LOGGER.info(f"Pack check response: {data}")
            return data.get("id")
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"HTTP Request failed: {e}")
            return None

    def save_check_id(self, check_id, pack_num):
        """
        上传待验证的ID
        """
        try:
            response = requests.post(
                self.url + "/save",
                json={"id": check_id, "num": pack_num},
                auth=HTTPBasicAuth(self.username, self.password),
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            LOGGER.info(f"Pack upload response: {data}")
            return True
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"HTTP Request failed: {e}")
            return False

    def set_valid(self, check_id, valid):
        """
        设置验证结果
        """
        try:
            response = requests.post(
                self.url + "/set_valid",
                json={"id": check_id, "valid": valid},
                auth=HTTPBasicAuth(self.username, self.password),
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            LOGGER.info(f"Pack valid response: {data}")
            return True
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"HTTP Request failed: {e}")
            return False

    def get_valid(self, check_id):
        """
        获取验证结果
        """
        try:
            response = requests.get(
                self.url + "/get_valid",
                params={"id": check_id},
                auth=HTTPBasicAuth(self.username, self.password),
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            LOGGER.info(f"Pack get valid response: {data}")
            return data.get("valid")
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"HTTP Request failed: {e}")
            return None
