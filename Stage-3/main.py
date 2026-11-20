# Phụ trách: Nguyễn Trần Khánh Vinh

import os
import sys
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.entities import SessionManager
from dao.db import DatabaseHandler
from dao.user_dao import UserDAO
from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO
from services.auth_admin_service import AuthService, AdminService
from services.contact_group_service import ContactService, GroupService
from views.login_dashboard import LoginDashboardView
from views.contact_view import ContactView
from views.group_favorite_view import GroupFavoriteView
from views.admin_view import AdminView


class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book Management System")
        self.root.geometry("1080x660")
        self.root.minsize(960, 600)
        self.session = SessionManager()
        self.db_handler = DatabaseHandler()
        self.user_dao = UserDAO(self.db_handler)
        self.contact_dao = ContactDAO(self.db_handler)
        self.group_dao = GroupDAO(self.db_handler)
        self.auth_service = AuthService(self.user_dao)
        self.admin_service = AdminService(self.user_dao, self.contact_dao, self.group_dao)
        self.contact_service = ContactService(self.contact_dao)
        self.group_service = GroupService(self.group_dao)
        self.current_user_id = "U01"
        self.current_user = None
        self.current_role = None
        self.current_screen = None
        self.nav_buttons = {}
        self.main_container = tk.Frame(self.root, bg="#e0f2fe")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.content_area = None
        self.login_dashboard_view = LoginDashboardView(self)
        self.contact_view = ContactView(self)
        self.group_favorite_view = GroupFavoriteView(self)
        self.admin_view = AdminView(self)
        self.login_dashboard_view.render_login_screen()

    def clear_window(self):
        for w in self.main_container.winfo_children():
            w.destroy()

    def clear_content_area(self):
        if self.content_area:
            for w in self.content_area.winfo_children():
                w.destroy()

    def render_main_layout(self):
        self.clear_window()
        self.main_container.config(bg="#ffffff")

        sb = tk.Frame(self.main_container, bg="#0f172a", width=230)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        brand = tk.Frame(sb, bg="#0f172a", pady=22)
        brand.pack(fill=tk.X, padx=18)
        tk.Label(brand, text="📇 Phone Book", font=("Arial", 14, "bold"), bg="#0f172a", fg="#ffffff", anchor="w").pack(fill=tk.X)
        tk.Label(brand, text="Management System", font=("Arial", 9), bg="#0f172a", fg="#94a3b8", anchor="w").pack(fill=tk.X)

        nav = tk.Frame(sb, bg="#0f172a")
        nav.pack(fill=tk.X, padx=12, pady=8)
        self.nav_buttons = {}
        for txt, key in [("🏠   Home", "Home"), ("👥   Contacts", "Contacts"), ("⭐   Favorites", "Favorites"), ("📁   Groups", "Groups"), ("⚙️   Admin", "Admin")]:
            b = tk.Button(
                nav, text=txt, font=("Arial", 11), bg="#0f172a", fg="#cbd5e1",
                bd=0, anchor="w", padx=14, pady=9, cursor="hand2", command=lambda k=key: self.switch_screen(k)
            )
            b.pack(fill=tk.X, pady=2)
            self.nav_buttons[key] = b

        foot = tk.Frame(sb, bg="#0f172a", pady=14)
        foot.pack(side=tk.BOTTOM, fill=tk.X, padx=14)
        tk.Button(foot, text="↪   Logout", font=("Arial", 11), bg="#0f172a", fg="#cbd5e1", bd=0, anchor="w", padx=10, pady=6, cursor="hand2", command=self.handle_logout).pack(fill=tk.X)
        tk.Frame(foot, bg="#1e293b", height=1).pack(fill=tk.X, pady=8)
        u_box = tk.Frame(foot, bg="#0f172a")
        u_box.pack(fill=tk.X)
        tk.Label(u_box, text="👤", font=("Arial", 14), bg="#2563eb", fg="#ffffff", padx=7, pady=3).pack(side=tk.LEFT, padx=(4, 8))
        u_txt = tk.Frame(u_box, bg="#0f172a")
        u_txt.pack(side=tk.LEFT)
        tk.Label(u_txt, text=self.current_user, font=("Arial", 10, "bold"), bg="#0f172a", fg="#ffffff", anchor="w").pack(fill=tk.X)
        tk.Label(u_txt, text=self.current_role, font=("Arial", 8), bg="#0f172a", fg="#94a3b8", anchor="w").pack(fill=tk.X)

        self.content_area = tk.Frame(self.main_container, bg="#ffffff")
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=32, pady=26)
        self.switch_screen("Home")

    def switch_screen(self, key):
        for k, b in self.nav_buttons.items():
            b.config(bg="#2563eb" if k == key else "#0f172a", fg="#ffffff" if k == key else "#cbd5e1", font=("Arial", 11, "bold" if k == key else "normal"))
        self.clear_content_area()
        self.current_screen = key
        screens = {
            "Home": self.login_dashboard_view.render_dashboard_content,
            "Contacts": self.contact_view.render_contacts_screen,
            "Favorites": self.group_favorite_view.render_favorites_screen,
            "Groups": self.group_favorite_view.render_groups_screen,
            "Admin": self.admin_view.render_admin_screen,
        }
        if key in screens:
            screens[key]()
            
    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.session.clear_session()
            self.current_user = self.current_role = None
            self.login_dashboard_view.render_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()
