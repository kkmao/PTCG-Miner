import logging
import sqlite3
import time
from packchecker import PackChecker


LOGGER = logging.getLogger("LocalChecker")


class LocalChecker(PackChecker):
    need_check = False

    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS data (
                    id TEXT PRIMARY KEY,
                    num INTEGER,
                    time INTEGER,
                    expiry_time INTEGER,
                    show_count INTEGER,
                    count INTEGER,
                    valid INTEGER
                )
                """
            )
            conn.commit()

    def get_check_id(self):
        """
        获取待验证的ID
        """
        if self.need_check:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, time FROM data
                WHERE (valid IS NULL OR valid = 0)
                ORDER BY time ASC
                """
            )
            rows = cursor.fetchall()

        if not rows:
            self.need_check = False
            return None

        # 检查count和show_count是否超过最大值
        for row in rows:
            max_count = self.get_max_count(row[1])
            max_show_count = self.get_max_show_count(row[1])
            # 如果count和show_count都没有超过最大值，返回该ID
            if row[5] < max_count and row[4] < max_show_count:
                check_id = row[0]
                break
            else:
                # 如果count超过最大值，将valid设置为-1
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                    UPDATE data
                    SET valid = -1
                    WHERE id = ?
                    """,
                        (row[0],),
                    )

        if not check_id:
            self.need_check = False
            return None

        # 更新count
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE data
                SET count = count + 1
                WHERE id = ?
                """,
                (check_id,),
            )
            conn.commit()
        return check_id

    def get_max_count(num):
        """
        获取最大验证次数
        """
        return num * 10

    def get_max_show_count(num):
        """
        获取最大其他包出现次数
        """
        if num == 1:
            return 5
        elif num == 2:
            return 9
        elif num == 3:
            return 15
        elif num == 4:
            return 21
        else:
            return num * 5

    def save_check_id(self, check_id, pack_num):
        """
        上传待验证的ID
        """
        # 校验check_id是否为16位纯数字
        if not check_id.isdigit() or len(check_id) != 16:
            return False

        _time = int(time.time())
        expiry_time = _time + 3 * 24 * 3600

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT OR REPLACE INTO data (id, num, time, expiry_time, show_count, count, valid)
            VALUES (?, ?, ?, ?, 0, 0, 0)
            """,
                (check_id, pack_num, _time, expiry_time),
            )
            conn.commit()
            self.need_check = True
            return True

    def set_valid(self, check_id, valid):
        """
        设置验证结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 如果valid为1或-1，更新valid
            if valid == 1 or valid == -1:
                cursor.execute(
                    """
                UPDATE data
                SET valid = ?
                WHERE id = ?
                """,
                    (valid, check_id),
                )
            # 如果valid为0，出现其他包，show_count加1
            elif valid == 0:
                cursor.execute(
                    """
                UPDATE data
                SET show_count = show_count + 1
                WHERE id = ?
                """,
                    (check_id),
                )
            else:
                return False
        conn.commit()
        return True

    def get_valid(self, check_id):
        """
        获取验证结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT valid FROM data
                WHERE id = ?
                """,
                (check_id,),
            )
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
