# File: dao/db.py
# Phụ trách: Nguyễn Minh Thống (Cặp B) - Thiết lập kết nối & khởi tạo 4 bảng SQLite

import os
import sqlite3


class DatabaseHandler:
    def __init__(self, db_name="phonebook.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, db_name)
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql, params=(), fetch=False, one=False):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            if one:
                row = cur.fetchone()
                return dict(row) if row else None
            if fetch:
                return [dict(r) for r in cur.fetchall()]
            conn.commit()

    def init_database(self):
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS User (
                    userID VARCHAR(20) PRIMARY KEY, username VARCHAR(50),
                    passwordHash VARCHAR(100), role VARCHAR(20), isActive INTEGER
                );
                CREATE TABLE IF NOT EXISTS ContactGroup (
                    groupID VARCHAR(20) PRIMARY KEY, userID VARCHAR(20), groupName VARCHAR(50)
                );
                CREATE TABLE IF NOT EXISTS Contact (
                    contactID VARCHAR(20) PRIMARY KEY, userID VARCHAR(20), fullName VARCHAR(50),
                    phoneNumber CHAR(10), email VARCHAR(100), address VARCHAR(200),
                    note VARCHAR(250), isFavorite INTEGER, groupName VARCHAR(50)
                );
                CREATE TABLE IF NOT EXISTS GroupMember (
                    membershipID VARCHAR(20) PRIMARY KEY, groupID VARCHAR(20),
                    contactID VARCHAR(20), role VARCHAR(20), nickname VARCHAR(50)
                );
            """)
        if self.query("SELECT COUNT(*) as c FROM User", one=True)["c"] == 0:
            self.query("INSERT INTO User VALUES ('U01','admin','123456','Administrator',1)")
