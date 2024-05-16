import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return bool(self.cursor.fetchone())

    def get_user_id(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        self.conn.commit()

    def add_chat(self, chat_id):
        self.cursor.execute("INSERT INTO chat (chat_id) VALUES (?)", (chat_id,))
        self.conn.commit()

    def get_chat_id(self, chat_id):
        self.cursor.execute("SELECT id FROM chat WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def chat_exists(self, chat_id):
        self.cursor.execute("SELECT id FROM chat WHERE chat_id = ?", (chat_id,))
        return bool(self.cursor.fetchone())

    def name_in_chat(self, name, chat_id):
        self.cursor.execute("SELECT id FROM Names WHERE name = ? AND chat_id = ?", (name, self.get_chat_id(chat_id)))
        return bool(self.cursor.fetchone())

    def add_name(self, chat_id, name, telegram_id):
        self.cursor.execute("INSERT INTO Names (chat_id, name, telegram_id) VALUES (?, ?, ?)",
                            (self.get_chat_id(chat_id), name, telegram_id))
        self.conn.commit()

    def get_name_id(self, name, chat_id):
        self.cursor.execute("SELECT telegram_id FROM Names WHERE name = ? AND chat_id = ?", (name, self.get_chat_id(chat_id)))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_record(self, user_id, operation, value):
        self.cursor.execute("INSERT INTO records (users_id, operarion, value) VALUES (?, ?, ?)",
                            (self.get_user_id(user_id), operation == "+", value))
        self.conn.commit()

    def get_records(self, user_id, within="all"):
        query = """SELECT * FROM records WHERE users_id = ? AND date BETWEEN datetime('now', 'start of {}') AND datetime('now', 'localtime')""".format(within)
        self.cursor.execute(query, (self.get_user_id(user_id),))
        return self.cursor.fetchall()


    def close(self):
        self.conn.close()
