# Phụ trách: Nguyễn Minh Thống 

import uuid
from dao.db import DatabaseHandler

class GroupDAO:
    def __init__(self, db=None):
        self.db = db or DatabaseHandler()

    def get_all_groups(self, uid):
        groups = self.db.query("SELECT * FROM ContactGroup WHERE userID=? ORDER BY groupID ASC", (uid,), fetch=True)
        for g in groups:
            g["count"] = self.db.query(
                "SELECT COUNT(*) as c FROM Contact WHERE userID=? AND groupName=?",
                (uid, g["groupName"]), one=True
            )["c"]
        return groups

    def count_all_system_groups(self):
        return self.db.query("SELECT COUNT(*) as c FROM ContactGroup", one=True)["c"]

    def group_exists(self, uid, name, exclude_id=None):
        sql = "SELECT groupID FROM ContactGroup WHERE userID=? AND LOWER(groupName)=LOWER(?)"
        params = [uid, name]
        if exclude_id:
            sql += " AND groupID!=?"
            params.append(exclude_id)
        return self.db.query(sql, params, one=True) is not None

    def create_group(self, uid, name):
        gid = "G" + uuid.uuid4().hex[:6].upper()
        self.db.query("INSERT INTO ContactGroup VALUES (?,?,?)", (gid, uid, name))
        return gid

    def rename_group(self, gid, uid, old_name, new_name):
        self.db.query("UPDATE ContactGroup SET groupName=? WHERE groupID=?", (new_name, gid))
        self.db.query("UPDATE Contact SET groupName=? WHERE userID=? AND groupName=?", (new_name, uid, old_name))

    def delete_group(self, gid, uid, name):
        self.db.query("UPDATE Contact SET groupName='Unassigned' WHERE userID=? AND groupName=?", (uid, name))
        self.db.query("DELETE FROM GroupMember WHERE groupID=?", (gid,))
        self.db.query("DELETE FROM ContactGroup WHERE groupID=?", (gid,))

    def get_group_members(self, uid, gid, gname):
        return self.db.query(
            """SELECT c.contactID, c.fullName, c.phoneNumber,
                      COALESCE(gm.role,'Member') as memberRole, COALESCE(gm.nickname,'') as nickname
               FROM Contact c LEFT JOIN GroupMember gm ON c.contactID=gm.contactID AND gm.groupID=?
               WHERE c.userID=? AND c.groupName=?""",
            (gid, uid, gname), fetch=True
        )

    def assign_contact_to_group(self, gid, gname, cid, role="Member", nickname=""):
        self.db.query("UPDATE Contact SET groupName=? WHERE contactID=?", (gname, cid))
        ex = self.db.query("SELECT membershipID FROM GroupMember WHERE groupID=? AND contactID=?", (gid, cid), one=True)
        if ex:
            self.db.query("UPDATE GroupMember SET role=?, nickname=? WHERE membershipID=?", (role, nickname, ex["membershipID"]))
        else:
            mid = "M" + uuid.uuid4().hex[:6].upper()
            self.db.query("INSERT INTO GroupMember VALUES (?,?,?,?,?)", (mid, gid, cid, role, nickname))

    def remove_contact_from_group(self, gid, cid):
        self.db.query("UPDATE Contact SET groupName='Unassigned' WHERE contactID=?", (cid,))
        self.db.query("DELETE FROM GroupMember WHERE groupID=? AND contactID=?", (gid, cid))
