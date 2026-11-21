# Phụ trách: Vũ Trung Tiến 

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
from services.auth_admin_service import AuthService, AdminService
from models.entities import SessionManager

class TestAuthAndAdminService(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.tmp_db = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        self.db = DatabaseHandler(self.tmp_db)
        self.user_dao = UserDAO(self.db)
        self.contact_dao = ContactDAO(self.db)
        self.group_dao = GroupDAO(self.db)
        self.auth = AuthService(self.user_dao)
        self.admin = AdminService(self.user_dao, self.contact_dao, self.group_dao)

    def tearDown(self):
        if os.path.exists(self.tmp_db):
            os.remove(self.tmp_db)

    def test_login_valid_and_invalid(self):
        ok, _, user = self.auth.login("admin", "123456")
        self.assertTrue(ok)
        self.assertEqual(user["role"], "Administrator")

        ok_bad, msg_bad, _ = self.auth.login("admin", "wrong")
        self.assertFalse(ok_bad)
        self.assertIn("Invalid", msg_bad)

        ok_empty, _, _ = self.auth.login("", "")
        self.assertFalse(ok_empty)

    def test_register_and_duplicate_check(self):
        ok, _ = self.auth.register_account("vinh01", "123456")
        self.assertTrue(ok)
        ok_dup, msg_dup = self.auth.register_account("vinh01", "123456")
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

    def test_lock_unlock_and_role_permissions(self):
        self.auth.register_account("user01", "123456")
        user01 = self.user_dao.get_by_username("user01")
        ok, _ = self.admin.toggle_user_lock(user01, "admin")
        self.assertTrue(ok)
        ok_login, msg_login, _ = self.auth.login("user01", "123456")
        self.assertFalse(ok_login)
        self.assertIn("locked", msg_login)
        user01 = self.user_dao.get_by_username("user01")
        self.admin.toggle_user_lock(user01, "admin")
        self.assertTrue(self.auth.login("user01", "123456")[0])
        user01 = self.user_dao.get_by_username("user01")
        self.admin.toggle_user_role(user01, "admin")
        self.assertEqual(self.user_dao.get_by_username("user01")["role"], "Administrator")
        sm = SessionManager()
        sm.start_session(self.user_dao.get_by_username("user01"))
        self.assertTrue(sm.is_admin())

    def test_protect_primary_admin_and_statistics(self):
        admin_u = self.user_dao.get_by_username("admin")
        self.assertFalse(self.admin.toggle_user_lock(admin_u, "admin")[0])
        self.assertFalse(self.admin.delete_user(admin_u, "admin")[0])
        self.assertFalse(self.admin.toggle_user_role(admin_u, "admin")[0])
        stats = self.admin.get_system_statistics()
        self.assertEqual(stats["total_users"], 1)
        self.assertEqual(stats["active_users"], 1)
        self.assertEqual(stats["storage_type"], "SQLite Database")

if __name__ == "__main__":
    unittest.main(verbosity=2)
