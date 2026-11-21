# Phụ trách: Vũ Trung Tiến 

from dao.user_dao import UserDAO
from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO
from models.entities import Validator

class AuthService:
    def __init__(self, user_dao=None):
        self.user_dao = user_dao or UserDAO()

    def login(self, username, password):
        if not username or not password:
            return False, "Please enter both username and password.", None
        user = self.user_dao.get_by_credentials(username, password)
        if not user:
            return False, "Invalid username or password", None
        if int(user.get("isActive", 1)) == 0:
            return False, "This account has been locked by Administrator", None
        return True, "Login successful", user

    def register_account(self, username, password, role="User"):
        ok, err = Validator.validate_credentials(username, password)
        if not ok:
            return False, err
        if self.user_dao.get_by_username(username):
            return False, f"Username '{username}' already exists."
        self.user_dao.create_user(username, password, role)
        return True, f"Account '{username}' created successfully."

class AdminService:
    def __init__(self, user_dao=None, contact_dao=None, group_dao=None):
        self.user_dao = user_dao or UserDAO()
        self.contact_dao = contact_dao or ContactDAO()
        self.group_dao = group_dao or GroupDAO()

    def get_system_statistics(self):
        users = self.user_dao.get_all_users()
        active = sum(1 for u in users if int(u.get("isActive", 1)) == 1)
        return {
            "total_users": len(users),
            "active_users": active,
            "locked_users": len(users) - active,
            "total_contacts": self.contact_dao.count_all_system_contacts(),
            "total_groups": self.group_dao.count_all_system_groups(),
            "storage_type": "SQLite Database",
        }

    def get_all_users(self, kw=""):
        kw = kw.strip().lower()
        users = self.user_dao.get_all_users()
        return [u for u in users if kw in u["username"].lower() or kw in u["role"].lower()] if kw else users

    def _is_protected(self, user, cur_admin):
        return user["username"] in ("admin", cur_admin)

    def update_user_account(self, user, new_pass, new_role, cur_admin):
        if not new_pass or len(new_pass) < 4:
            return False, "Password must be at least 4 characters."
        if self._is_protected(user, cur_admin) and new_role != "Administrator":
            return False, "Cannot demote the primary or current Administrator!"
        self.user_dao.update_user_info(user["userID"], new_pass, new_role)
        return True, f"Account '{user['username']}' updated."

    def toggle_user_lock(self, user, cur_admin):
        if self._is_protected(user, cur_admin):
            return False, "Cannot lock the primary or current Administrator!"
        new_st = 0 if int(user["isActive"]) == 1 else 1
        self.user_dao.update_status(user["userID"], new_st)
        return True, f"Account '{user['username']}' {'unlocked' if new_st else 'locked'}."

    def toggle_user_role(self, user, cur_admin):
        if self._is_protected(user, cur_admin):
            return False, "Cannot change role of the primary or current Administrator!"
        new_role = "Administrator" if user["role"] == "User" else "User"
        self.user_dao.update_role(user["userID"], new_role)
        return True, f"Role of '{user['username']}' changed to {new_role}."

    def delete_user(self, user, cur_admin):
        if self._is_protected(user, cur_admin):
            return False, "Cannot delete the primary or current Administrator!"
        self.user_dao.delete_user(user["userID"])
        return True, f"Account '{user['username']}' deleted."
