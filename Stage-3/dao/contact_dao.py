# Phụ trách: Nguyễn Minh Thống 

import uuid
from dao.db import DatabaseHandler

class ContactDAO:
    def __init__(self, db=None):
        self.db = db or DatabaseHandler()

    def get_all_contacts(self, uid):
        return self.db.query("SELECT * FROM Contact WHERE userID=?", (uid,), fetch=True)

    def get_favorite_contacts(self, uid):
        return self.db.query("SELECT * FROM Contact WHERE userID=? AND isFavorite=1", (uid,), fetch=True)

    def count_all_system_contacts(self):
        return self.db.query("SELECT COUNT(*) as c FROM Contact", one=True)["c"]

    def phone_exists(self, phone, uid, exclude_id=None):
        sql = "SELECT contactID FROM Contact WHERE userID=? AND phoneNumber=?"
        params = [uid, str(phone)]
        if exclude_id:
            sql += " AND contactID!=?"
            params.append(exclude_id)
        return self.db.query(sql, params, one=True) is not None

    def add_contact(self, uid, name, phone, group="Unassigned", fav=0, email="", addr="", note=""):
        cid = "C" + uuid.uuid4().hex[:6].upper()
        self.db.query(
            "INSERT INTO Contact VALUES (?,?,?,?,?,?,?,?,?)",
            (cid, uid, name, str(phone), email, addr, note, int(fav), group),
        )
        return cid

    def update_contact(self, cid, name, phone, group="Unassigned", fav=0, email="", addr="", note=""):
        self.db.query(
            "UPDATE Contact SET fullName=?, phoneNumber=?, groupName=?, isFavorite=?, email=?, address=?, note=? WHERE contactID=?",
            (name, str(phone), group, int(fav), email, addr, note, cid),
        )

    def toggle_favorite(self, cid, fav):
        self.db.query("UPDATE Contact SET isFavorite=? WHERE contactID=?", (int(fav), cid))

    def delete_contact(self, cid):
        self.db.query("DELETE FROM GroupMember WHERE contactID=?", (cid,))
        self.db.query("DELETE FROM Contact WHERE contactID=?", (cid,))
