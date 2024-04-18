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
