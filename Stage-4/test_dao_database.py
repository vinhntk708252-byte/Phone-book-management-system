# Phụ trách: Nguyễn Minh Thống 

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dao.db import DatabaseHandler
from dao.user_dao import UserDAO
from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO

class TestDatabaseAndDAO(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.tmp_db = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        self.db = DatabaseHandler(self.tmp_db)
        self.user_dao = UserDAO(self.db)
        self.contact_dao = ContactDAO(self.db)
        self.group_dao = GroupDAO(self.db)

    def tearDown(self):
        if os.path.exists(self.tmp_db):
            os.remove(self.tmp_db)

    def test_default_admin_created(self):
        admin = self.user_dao.get_by_credentials("admin", "123456")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "Administrator")
        self.assertEqual(int(admin["isActive"]), 1)

    def test_phone_preserves_leading_zero_and_unicode(self):
        cid = self.contact_dao.add_contact(
            "U01", "Nguyễn Văn Ân", "0901234567", "Gia Đình", 1, "an@gmail.com", "TP.HCM", "Ghi chú"
        )
        contacts = self.contact_dao.get_all_contacts("U01")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["contactID"], cid)
        self.assertEqual(contacts[0]["phoneNumber"], "0901234567")
        self.assertEqual(contacts[0]["fullName"], "Nguyễn Văn Ân")

    def test_group_rename_and_delete_preserves_contacts(self):
        gid = self.group_dao.create_group("U01", "Family")
        cid = self.contact_dao.add_contact("U01", "An", "0901112222", "Family")
        self.group_dao.assign_contact_to_group(gid, "Family", cid, "Leader", "Anh An")

        members = self.group_dao.get_group_members("U01", gid, "Family")
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["nickname"], "Anh An")

        self.group_dao.rename_group(gid, "U01", "Family", "Relatives")
        self.assertEqual(self.contact_dao.get_all_contacts("U01")[0]["groupName"], "Relatives")

        self.group_dao.delete_group(gid, "U01", "Relatives")
        contacts = self.contact_dao.get_all_contacts("U01")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["groupName"], "Unassigned")

    def test_delete_user_cascades_contacts_and_groups(self):
        uid = self.user_dao.create_user("user01", "123456", "User")
        self.group_dao.create_group(uid, "Work")
        self.contact_dao.add_contact(uid, "Bob", "0912345678", "Work")
        self.user_dao.delete_user(uid)
        self.assertIsNone(self.user_dao.get_by_username("user01"))
        self.assertEqual(len(self.contact_dao.get_all_contacts(uid)), 0)
        self.assertEqual(len(self.group_dao.get_all_groups(uid)), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
