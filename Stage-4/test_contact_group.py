# Phụ trách: Nguyễn Quốc Cường

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dao.db import DatabaseHandler
from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO
from services.contact_group_service import ContactService, GroupService

class TestContactAndGroupService(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.tmp_db = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        self.db = DatabaseHandler(self.tmp_db)
        self.cs = ContactService(ContactDAO(self.db))
        self.gs = GroupService(GroupDAO(self.db))

    def tearDown(self):
        if os.path.exists(self.tmp_db):
            os.remove(self.tmp_db)

    def test_add_validation_and_duplicate_rules(self):
        self.assertFalse(self.cs.validate_and_save("U01", "", "0901234567")[0])
        self.assertFalse(self.cs.validate_and_save("U01", "An", "12345")[0])
        self.assertFalse(self.cs.validate_and_save("U01", "An", "0901234567", email="bad-email")[0])
        self.assertTrue(self.cs.validate_and_save("U01", "Nguyen Van An", "0901234567", "Friends", True)[0])
        self.assertTrue(self.cs.validate_and_save("U01", "Nguyen Van An", "0987654321", "Family", False)[0])
        ok_dup, msg_dup = self.cs.validate_and_save("U01", "Tran Thi B", "0901234567", "Work", False)
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

    def test_search_sort_pagination_and_favorites(self):
        for i in range(7):
            self.cs.validate_and_save("U01", f"Contact {7 - i}", f"090000000{i}", "Friends", fav=(i % 2 == 0))

        res = self.cs.search_contacts("Contact 1", "U01")
        self.assertEqual(len(res), 1)
        self.assertEqual(len(self.cs.search_contacts("NOT_FOUND", "U01")), 0)

        all_c = self.cs.get_contacts_for_ui("U01")
        asc = self.cs.sort_contacts(all_c, by="name", ascending=True)
        desc = self.cs.sort_contacts(all_c, by="name", ascending=False)
        self.assertEqual(asc[0]["name"], "Contact 1")
        self.assertEqual(desc[0]["name"], "Contact 7")

        p1, cur1, total = self.cs.paginate_contacts(asc, page=1, page_size=5)
        p2, cur2, _ = self.cs.paginate_contacts(asc, page=2, page_size=5)
        self.assertEqual((len(p1), cur1, total), (5, 1, 2))
        self.assertEqual((len(p2), cur2), (2, 2))

        favs = self.cs.get_favorites_for_ui("U01")
        self.assertEqual(len(favs), 4)

    def test_group_crud_and_duplicate_group(self):
        self.assertTrue(self.gs.create_group("U01", "Family")[0])
        self.assertFalse(self.gs.create_group("U01", "family")[0])
        g = self.gs.get_groups_for_ui("U01")[0]
        self.assertTrue(self.gs.rename_group("U01", g["id"], "Family", "VIP")[0])
        self.assertEqual(self.gs.get_groups_for_ui("U01")[0]["name"], "VIP")
        self.assertTrue(self.gs.delete_group("U01", g["id"], "VIP")[0])
        self.assertEqual(len(self.gs.get_groups_for_ui("U01")), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
