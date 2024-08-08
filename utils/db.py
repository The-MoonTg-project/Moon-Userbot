#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import json
import threading
import sqlite3
from dns import resolver
import pymongo
from utils import config

resolver.default_resolver = resolver.Resolver(configure=False)
resolver.default_resolver.nameservers = ["1.1.1.1"]


class Database:
    def get(self, module: str, variable: str, default=None):
        """Get value from database"""
        raise NotImplementedError

    def set(self, module: str, variable: str, value):
        """Set key in database"""
        raise NotImplementedError

    def remove(self, module: str, variable: str):
        """Remove key from database"""
        raise NotImplementedError

    def get_collection(self, module: str) -> dict:
        """Get database for selected module"""
        raise NotImplementedError

    def close(self):
        """Close the database"""
        raise NotImplementedError


class MongoDatabase(Database):
    def __init__(self, url, name):
        self._client = pymongo.MongoClient(url)
        self._database = self._client[name]

    def set(self, module: str, variable: str, value):
        if not isinstance(module, str) or not isinstance(variable, str):
            raise ValueError("Module and variable must be strings")
        self._database[module].replace_one(
            {"var": variable}, {"var": variable, "val": value}, upsert=True
        )

    def get(self, module: str, variable: str, default=None):
        if not isinstance(module, str) or not isinstance(variable, str):
            raise ValueError("Module and variable must be strings")
        doc = self._database[module].find_one({"var": variable})
        return default if doc is None else doc["val"]

    def get_collection(self, module: str):
        if not isinstance(module, str):
            raise ValueError("Module must be a string")
        return {item["var"]: item["val"] for item in self._database[module].find()}

    def remove(self, module: str, variable: str):
        if not isinstance(module, str) or not isinstance(variable, str):
            raise ValueError("Module and variable must be strings")
        self._database[module].delete_one({"var": variable})

    def close(self):
        self._client.close()

    def add_chat_history(self, user_id, message):
        chat_history = self.get_chat_history(user_id, default=[])
        chat_history.append(message)
        self.set(f"core.cohere.user_{user_id}", "chat_history", chat_history)

    def get_chat_history(self, user_id, default=None):
        if default is None:
            default = []
        return self.get(f"core.cohere.user_{user_id}", "chat_history", default=[])

    def addaiuser(self, user_id):
        chatai_users = self.get("core.chatbot", "chatai_users", default=[])
        if user_id not in chatai_users:
            chatai_users.append(user_id)
            self.set("core.chatbot", "chatai_users", chatai_users)

    def remaiuser(self, user_id):
        chatai_users = self.get("core.chatbot", "chatai_users", default=[])
        if user_id in chatai_users:
            chatai_users.remove(user_id)
            self.set("core.chatbot", "chatai_users", chatai_users)

    def getaiusers(self):
        return self.get("core.chatbot", "chatai_users", default=[])


class SqliteDatabase(Database):
    def __init__(self, file):
        self._conn = sqlite3.connect(file, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        self._lock = threading.Lock()

    @staticmethod
    def _parse_row(row: sqlite3.Row):
        if row["type"] == "bool":
            return row["val"] == "1"
        if row["type"] == "int":
            return int(row["val"])
        if row["type"] == "str":
            return row["val"]
        return json.loads(row["val"])

    def _execute(self, module: str, *args, **kwargs) -> sqlite3.Cursor:
        pattern = r"^(core|custom)"
        if not re.match(pattern, module):
            raise ValueError(f"Invalid module name format: {module}")

        self._lock.acquire()
        try:
            cursor = self._conn.cursor()
            return cursor.execute(*args, **kwargs)
        except sqlite3.OperationalError as e:
            if str(e).startswith("no such table"):
                sql = f"""
                CREATE TABLE IF NOT EXISTS '{module}' (
                var TEXT UNIQUE NOT NULL,
                val TEXT NOT NULL,
                type TEXT NOT NULL
                )
                """
                cursor = self._conn.cursor()
                cursor.execute(sql)
                self._conn.commit()
                return cursor.execute(*args, **kwargs)
            raise e from None
        finally:
            self._lock.release()

    def get(self, module: str, variable: str, default=None):
        sql = f"SELECT * FROM '{module}' WHERE var=?"
        cur = self._execute(module, sql, (variable,))

        row = cur.fetchone()
        if row is None:
            return default
        return self._parse_row(row)

    def set(self, module: str, variable: str, value) -> bool:
        sql = f"""
        INSERT INTO '{module}' VALUES ( ?, ?, ? )
        ON CONFLICT (var) DO
        UPDATE SET val=?, type=? WHERE var=?
        """

        if isinstance(value, bool):
            val = "1" if value else "0"
            typ = "bool"
        elif isinstance(value, str):
            val = value
            typ = "str"
        elif isinstance(value, int):
            val = str(value)
            typ = "int"
        else:
            val = json.dumps(value)
            typ = "json"

        self._execute(module, sql, (variable, val, typ, val, typ, variable))
        self._conn.commit()

        return True

    def remove(self, module: str, variable: str):
        sql = f"DELETE FROM '{module}' WHERE var=?"
        self._execute(module, sql, (variable,))
        self._conn.commit()

    def get_collection(self, module: str) -> dict:
        pattern = r"^(core|custom)"
        if not re.match(pattern, module):
            raise ValueError(f"Invalid module name format: {module}")

        sql = f"SELECT * FROM '{module}'"
        cur = self._execute(module, sql)

        collection = {}
        for row in cur:
            collection[row["var"]] = self._parse_row(row)

        return collection

    def close(self):
        self._conn.commit()
        self._conn.close()

    def add_chat_history(self, user_id, message):
        chat_history = self.get_chat_history(user_id, default=[])
        chat_history.append(message)
        self.set(f"core.cohere.user_{user_id}", "chat_history", chat_history)

    def get_chat_history(self, user_id, default=None):
        if default is None:
            default = []
        return self.get(f"core.cohere.user_{user_id}", "chat_history", default=[])

    def addaiuser(self, user_id):
        chatai_users = self.get("core.chatbot", "chatai_users", default=[])
        if user_id not in chatai_users:
            chatai_users.append(user_id)
            self.set("core.chatbot", "chatai_users", chatai_users)

    def remaiuser(self, user_id):
        chatai_users = self.get("core.chatbot", "chatai_users", default=[])
        if user_id in chatai_users:
            chatai_users.remove(user_id)
            self.set("core.chatbot", "chatai_users", chatai_users)

    def getaiusers(self):
        return self.get("core.chatbot", "chatai_users", default=[])


if config.db_type in ["mongo", "mongodb"]:
    db = MongoDatabase(config.db_url, config.db_name)
else:
    db = SqliteDatabase(config.db_name)
