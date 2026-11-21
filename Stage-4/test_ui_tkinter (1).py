# Phụ trách: Bùi Lê Giang 

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dao.db import DatabaseHandler
from dao.user_dao import UserDAO
from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO
from services.auth_admin_service import AuthService, AdminService
from services.contact_group_service import ContactService, GroupService
from models.entities import SessionManager
from views.contact_view import ContactView
from views.login_dashboard import LoginDashboardView
from views.group_favorite_view import GroupFavoriteView
from views.admin_view import AdminView

class TestTkinterViewsAndUIState(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.tmp_db = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        self.db = DatabaseHandler(self.tmp_db)
        self.mock_app = MagicMock()
        self.mock_app.session = SessionManager()
        self.mock_app.auth_service = AuthService(UserDAO(self.db))
        self.mock_app.contact_service = ContactService(ContactDAO(self.db))
        self.mock_app.group_service = GroupService(GroupDAO(self.db))
        self.mock_app.admin_service = AdminService(UserDAO(self.db), ContactDAO(self.db), GroupDAO(self.db))
        self.mock_app.current_user_id = "U01"
        self.mock_app.current_user = "admin"
        self.mock_app.current_role = "Administrator"

    def tearDown(self):
        if os.path.exists(self.tmp_db):
            os.remove(self.tmp_db)

    def test_contact_view_sort_and_pagination_state(self):
        view = ContactView(self.mock_app)
        self.assertEqual((view.sort_by, view.sort_asc, view.page), ("name", True, 1))

        view._toggle_sort() 
        self.assertEqual((view.sort_by, view.sort_asc), ("name", False))
        view._toggle_sort() 
        self.assertEqual((view.sort_by, view.sort_asc), ("phone", True))
        view._toggle_sort() 
        self.assertEqual((view.sort_by, view.sort_asc), ("name", True))

        view._go_page(1, total=3)
        self.assertEqual(view.page, 2)
        view._go_page(-1, total=3)
        self.assertEqual(view.page, 1)
        view._go_page(-1, total=3) 
        self.assertEqual(view.page, 1)

    @patch("views.contact_view.messagebox.showinfo")
    def test_contact_view_show_details_popup(self, mock_info):
        view = ContactView(self.mock_app)
        sample = {
            "id": "C001", "name": "Nguyen Van An", "phone": "0901234567",
            "email": "an@gmail.com", "address": "HCMC", "group": "Friends",
            "favorite": True, "note": "Classmate"
        }
        view.show_details(sample)
        mock_info.assert_called_once()
        title, body = mock_info.call_args[0]
        self.assertEqual(title, "Contact Details")
        self.assertIn("0901234567", body)
        self.assertIn("Nguyen Van An", body)

    @patch("views.contact_view.messagebox.askyesno", return_value=False)
    def test_delete_contact_cancel_does_not_delete(self, mock_confirm):
        self.mock_app.contact_service.validate_and_save("U01", "An", "0901234567")
        c = self.mock_app.contact_service.get_contacts_for_ui("U01")[0]
        view = ContactView(self.mock_app)
        view.delete_contact(c)
        self.assertEqual(len(self.mock_app.contact_service.get_contacts_for_ui("U01")), 1)

    def test_login_view_handle_login_success(self):
        view = LoginDashboardView(self.mock_app)
        view.u_ent = MagicMock()
        view.p_ent = MagicMock()
        view.u_ent.get.return_value = "admin"
        view.p_ent.get.return_value = "123456"
        view.handle_login()
        self.assertEqual(self.mock_app.current_user, "admin")
        self.assertTrue(self.mock_app.session.is_admin())
        self.mock_app.render_main_layout.assert_called_once()

    def test_all_view_classes_instantiate_cleanly(self):
        self.assertIsNotNone(GroupFavoriteView(self.mock_app))
        self.assertIsNotNone(AdminView(self.mock_app))

if __name__ == "__main__":
    unittest.main(verbosity=2)
