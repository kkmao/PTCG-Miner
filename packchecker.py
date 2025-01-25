from abc import ABC, abstractmethod


class PackChecker(ABC):
    @abstractmethod
    def get_check_id(self):
        pass

    @abstractmethod
    def save_check_id(self, check_id, pack_num):
        pass

    @abstractmethod
    def set_valid(self, check_id, valid):
        pass

    @abstractmethod
    def get_valid(self, check_id):
        pass
