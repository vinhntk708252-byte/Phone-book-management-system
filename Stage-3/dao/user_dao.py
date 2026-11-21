# Phụ trách: Nguyễn Minh Thống 

import uuid
from dao.db import DatabaseHandler

class UserDAO:
    def __init__(self, db=None):
        self.db = db or DatabaseHandler()

    def get_by_credentials(self, u, p):
        return self.db.query("SELECT * FROM User WHERE username=? AND passwordHash=?", (u, p), one=True)

    def get_by_username(self, u):
        return self.db.query("SELECT * FROM User WHERE LOWER(username)=LOWER(?)", (u,), one=True)

    def get_all_users(self):
        return self.db.query("SELECT * FROM User ORDER BY userID ASC", fetch=True)

    def create_user(self, u, p, role="User"):
        uid = "U" + uuid.uuid4().hex[:6].upper()
        self.db.query("INSERT INTO User VALUES (?, ?, ?, ?, 1)", (uid, u, p, role))
        return uid

    def update_user_info(self, uid, p, role):
        self.db.query("UPDATE User SET passwordHash=?, role=? WHERE userID=?", (p, role, uid))

    def update_status(self, uid, active):
        self.db.query("UPDATE User SET isActive=? WHERE userID=?", (int(active), uid))

    def update_role(self, uid, role):
        self.db.query("UPDATE User SET role=? WHERE userID=?", (role, uid))

    def delete_user(self, uid):
        self.db.query("DELETE FROM GroupMember WHERE contactID IN (SELECT contactID FROM Contact WHERE userID=?)", (uid,))
        self.db.query("DELETE FROM Contact WHERE userID=?", (uid,))
        self.db.query("DELETE FROM ContactGroup WHERE userID=?", (uid,))
        self.db.query("DELETE FROM User WHERE userID=?", (uid,))
