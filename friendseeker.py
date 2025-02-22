import json
import requests
from requests.auth import HTTPBasicAuth
import logging

LOGGER = logging.getLogger("FreindSeeker")


class FriendSeeker:
    def __init__(
        self,
        url=None,
        username=None,
        password=None,
        local_path=None,
        remote=False,
        local=True,
    ):
        self.remote = remote
        if remote:
            if url and username and password:
                self.url = url
                self.username = username
                self.password = password
            else:
                self.remote = False
                LOGGER.warning("No remote friend source specified")
        self.local = local
        if local:
            if local_path:
                self.local_path = local_path
            else:
                self.local = False
                LOGGER.warning("No local path specified")

    def get_friend_codes(self):
        """
        获取fc
        """
        friends = []
        if self.remote:
            friends += self.get_reomte_friend_codes()
        elif self.local:
            friends += self.get_local_friend_codes()
            # 去重
            friends = list(set(friends))
        else:
            LOGGER.error("No fc source specified")
        return friends

    def get_local_friend_codes(self):
        """
        从local_path的json文件获取fc
        """
        try:
            with open(self.local_path, "r") as f:
                data = json.load(f)
                LOGGER.info(f"Local fc: {data}")
                return data
        except Exception as e:
            LOGGER.error(f"Failed to read local fc: {e}")
            return []

    def get_reomte_friend_codes(self):
        """
        获取待验证的ID
        """
        try:
            response = requests.get(
                self.url + "/get_true_ids",
                auth=HTTPBasicAuth(self.username, self.password),
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            LOGGER.info(f"Pack check response: {data}")
            return data.get("ids", [])
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"HTTP Request failed: {e}")
            return []
