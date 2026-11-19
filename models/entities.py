# File: models/entities.py
# Phụ trách: Nguyễn Trần Khánh Vinh (Leader - Cặp C)
# Nhiệm vụ: Khởi tạo thực thể (Entities), Validator kiểm tra dữ liệu & SessionManager quản lý phiên

from dataclasses import dataclass


@dataclass
class User:
    userID: str
    username: str
    passwordHash: str
    role: str = "User"
    isActive: int = 1


@dataclass
class Group:
    groupID: str
    userID: str
    groupName: str


@dataclass
class Contact:
    contactID: str
    userID: str
    fullName: str
    phoneNumber: str
    email: str = ""
    address: str = ""
    note: str = ""
    isFavorite: int = 0
    groupName: str = "Unassigned"


@dataclass
class GroupMember:
    membershipID: str
    groupID: str
    contactID: str
    role: str = "Member"
    nickname: str = ""


class Validator:
    """Kiểm tra tính hợp lệ dữ liệu đầu vào theo mục 5.1 Architecture Design."""

    @staticmethod
    def validate_credentials(username: str, password: str):
        if not username or not password:
            return False, "Username and password cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        return True, ""

    @staticmethod
    def validate_contact_input(name: str, phone: str, email: str = ""):
        if not name or not phone:
            return False, "Full Name and Phone Number are required fields."
        if not phone.isdigit() or len(phone) != 10 or not phone.startswith("0"):
            return False, "Phone number must contain 10 digits and start with '0'."
        if email and ("@" not in email or "." not in email):
            return False, "Invalid email format (e.g., example@gmail.com)."
        return True, ""


class SessionManager:
    """Quản lý phiên đăng nhập và phân quyền (Access Control) theo mục 5.1."""

    def __init__(self):
        self.user_id = None
        self.username = None
        self.role = None

    def start_session(self, user_dict: dict):
        self.user_id = user_dict["userID"]
        self.username = user_dict["username"]
        self.role = user_dict["role"]

    def clear_session(self):
        self.user_id = None
        self.username = None
        self.role = None

    def is_admin(self) -> bool:
        return self.role == "Administrator"
