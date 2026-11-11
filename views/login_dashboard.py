import tkinter as tk
from tkinter import messagebox
class LoginAndDashboardUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book Management System")
        self.root.geometry("1050x650")
        self.root.minsize(950, 600)

        # Lưu thông tin người dùng và trạng thái màn hình hiện tại
        self.current_user = None
        self.current_role = None
        self.current_screen = None

        # Khung chứa chính của ứng dụng
        self.main_container = tk.Frame(self.root, bg="#e0f2fe")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Khởi chạy màn hình Login đầu tiên
        self.show_login_screen()

    def clear_window(self):
        """Xóa các thành phần trên màn hình hiện tại để chuyển trang."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ==================== 1. MÀN HÌNH LOGIN (MỤC 7.1) ====================
    def show_login_screen(self):
        self.clear_window()
        self.current_screen = "Login"
        self.main_container.config(bg="#e0f2fe")

        # Khung trắng căn giữa màn hình
        self.login_card = tk.Frame(
            self.main_container, bg="#ffffff", bd=1, relief=tk.SOLID
        )
        self.login_card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=420, height=510)

        # Biểu tượng & Tiêu đề
        tk.Label(
            self.login_card,
            text="📇",
            font=("Arial", 28),
            bg="#eff6ff",
            fg="#2563eb",
            padx=12,
            pady=6,
        ).pack(pady=(30, 10))

        self.title_label = tk.Label(
            self.login_card,
            text="Phone Book Management",
            font=("Arial", 17, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        )
        self.title_label.pack(pady=(0, 15))

        # Thanh báo lỗi màu đỏ (Mặc định ẩn, hiện ra khi nhập sai)
        self.error_banner = tk.Frame(
            self.login_card, bg="#fef2f2", highlightbackground="#fecaca", highlightthickness=1
        )
        self.error_label = tk.Label(
            self.error_banner,
            text="ⓘ  Invalid username or password",
            font=("Arial", 10),
            bg="#fef2f2",
            fg="#dc2626",
            padx=12,
            pady=8,
        )
        self.error_label.pack(anchor="w")

        # Khu vực nhập Username & Password
        form_frame = tk.Frame(self.login_card, bg="#ffffff")
        form_frame.pack(fill=tk.X, padx=35, pady=5)

        tk.Label(
            form_frame,
            text="Username",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#334155",
            anchor="w",
        ).pack(fill=tk.X, pady=(5, 5))

        self.username_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            bg="#f8fafc",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1,
        )
        self.username_entry.pack(fill=tk.X, ipady=7, pady=(0, 15))
        self.username_entry.insert(0, "admin")

        tk.Label(
            form_frame,
            text="Password",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#334155",
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            bg="#f8fafc",
            fg="#0f172a",
            show="•",
            relief=tk.SOLID,
            bd=1,
        )
        self.password_entry.pack(fill=tk.X, ipady=7, pady=(0, 22))
        self.password_entry.insert(0, "123456")

        # Nút Login
        self.login_btn = tk.Button(
            form_frame,
            text="Login",
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.handle_login,
        )
        self.login_btn.pack(fill=tk.X, ipady=9, pady=(0, 10))

        # Nút Create Account
        self.create_acc_btn = tk.Button(
            form_frame,
            text="Create Account",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#334155",
            activebackground="#f1f5f9",
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",
            command=lambda: messagebox.showinfo(
                "Create Account", "Chức năng tạo tài khoản mới."
            ),
        )
        self.create_acc_btn.pack(fill=tk.X, ipady=8)

        # Cho phép bấm phím Enter để đăng nhập
        self.root.bind("<Return>", lambda event: self.handle_login())

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Tài khoản mặc định để vào Dashboard: admin / 123456
        if username == "admin" and password == "123456":
            self.current_user = "admin"
            self.current_role = "Administrator"
            self.root.unbind("<Return>")
            self.show_home_dashboard()
        else:
            # Hiện thông báo lỗi màu đỏ phía trên ô Username
            self.error_banner.pack(
                fill=tk.X, padx=35, pady=(0, 10), before=self.username_entry.master
            )

    # ==================== 2. MÀN HÌNH HOME DASHBOARD (MỤC 7.2) ====================
    def show_home_dashboard(self):
        self.clear_window()
        self.current_screen = "Dashboard"
        self.main_container.config(bg="#ffffff")

        # --- THANH SIDEBAR BÊN TRÁI ---
        self.sidebar = tk.Frame(self.main_container, bg="#0f172a", width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Tên hệ thống trên Sidebar
        brand_box = tk.Frame(self.sidebar, bg="#0f172a", pady=25)
        brand_box.pack(fill=tk.X, padx=20)

        tk.Label(
            brand_box,
            text="📇 Phone Book",
            font=("Arial", 14, "bold"),
            bg="#0f172a",
            fg="#ffffff",
            anchor="w",
        ).pack(fill=tk.X)
        tk.Label(
            brand_box,
            text="Management System",
            font=("Arial", 9),
            bg="#0f172a",
            fg="#94a3b8",
            anchor="w",
        ).pack(fill=tk.X, pady=(2, 0))

        # Các nút điều hướng trên Sidebar
        nav_frame = tk.Frame(self.sidebar, bg="#0f172a")
        nav_frame.pack(fill=tk.X, padx=12, pady=10)

        self.nav_buttons = {}
        menu_items = [
            ("🏠   Home", "Home", True),
            ("👥   Contacts", "Contacts", False),
            ("⭐   Favorites", "Favorites", False),
            ("📁   Groups", "Groups", False),
            ("⚙️   Admin", "Admin", False),
        ]

        for label_text, key_name, is_active in menu_items:
            btn = tk.Button(
                nav_frame,
                text=label_text,
                font=("Arial", 11, "bold") if is_active else ("Arial", 11),
                bg="#2563eb" if is_active else "#0f172a",
                fg="#ffffff" if is_active else "#cbd5e1",
                activebackground="#1e293b",
                activeforeground="#ffffff",
                bd=0,
                anchor="w",
                padx=16,
                pady=10,
                cursor="hand2",
            )
            btn.pack(fill=tk.X, pady=3)
            self.nav_buttons[key_name] = btn

        # Khu vực Logout & Thông tin User ở đáy Sidebar
        sidebar_footer = tk.Frame(self.sidebar, bg="#0f172a", pady=15)
        sidebar_footer.pack(side=tk.BOTTOM, fill=tk.X, padx=15)

        self.logout_btn = tk.Button(
            sidebar_footer,
            text="↪   Logout",
            font=("Arial", 11),
            bg="#0f172a",
            fg="#cbd5e1",
            activebackground="#1e293b",
            activeforeground="#ef4444",
            bd=0,
            anchor="w",
            padx=10,
            pady=8,
            cursor="hand2",
            command=self.handle_logout,
        )
        self.logout_btn.pack(fill=tk.X, pady=(0, 10))

        tk.Frame(sidebar_footer, bg="#1e293b", height=1).pack(fill=tk.X, pady=8)

        user_info = tk.Frame(sidebar_footer, bg="#0f172a")
        user_info.pack(fill=tk.X, pady=5)

        tk.Label(
            user_info,
            text="👤",
            font=("Arial", 16),
            bg="#2563eb",
            fg="#ffffff",
            padx=8,
            pady=4,
        ).pack(side=tk.LEFT, padx=(5, 10))

        user_text = tk.Frame(user_info, bg="#0f172a")
        user_text.pack(side=tk.LEFT, fill=tk.X)
        tk.Label(
            user_text,
            text=self.current_user,
            font=("Arial", 11, "bold"),
            bg="#0f172a",
            fg="#ffffff",
            anchor="w",
        ).pack(fill=tk.X)
        tk.Label(
            user_text,
            text=self.current_role,
            font=("Arial", 9),
            bg="#0f172a",
            fg="#94a3b8",
            anchor="w",
        ).pack(fill=tk.X)

        # --- VÙNG NỘI DUNG DASHBOARD BÊN PHẢI ---
        content_area = tk.Frame(self.main_container, bg="#ffffff")
        content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=35)

        self.dashboard_title = tk.Label(
            content_area,
            text="Dashboard",
            font=("Arial", 22, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        )
        self.dashboard_title.pack(anchor="w", pady=(0, 25))

        # Lưới 4 thẻ thống kê (2 hàng x 2 cột)
        cards_grid = tk.Frame(content_area, bg="#ffffff")
        cards_grid.pack(fill=tk.X, pady=(0, 25))
        cards_grid.columnconfigure(0, weight=1)
        cards_grid.columnconfigure(1, weight=1)

        self.summary_cards = {}
        self.create_summary_card(
            cards_grid, "👥", "My Contacts", "12 contacts", "#eff6ff", "#bfdbfe", "#2563eb", 0, 0
        )
        self.create_summary_card(
            cards_grid, "⭐", "Favorites", "3 contacts", "#fefce8", "#fef08a", "#eab308", 0, 1
        )
        self.create_summary_card(
            cards_grid, "📁", "Groups", "3 groups", "#f0fdf4", "#bbf7d0", "#16a34a", 1, 0
        )
        self.create_summary_card(
            cards_grid, "⊕", "Add Contact", "Create new", "#faf5ff", "#e9d5ff", "#9333ea", 1, 1
        )

        # Thanh nút bấm nhanh bên dưới 4 thẻ
        action_bar = tk.Frame(
            content_area,
            bg="#f8fafc",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            padx=20,
            pady=18,
        )
        action_bar.pack(fill=tk.X)

        self.quick_add_btn = tk.Button(
            action_bar,
            text="+   Add Contact",
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
        )
        self.quick_add_btn.pack(side=tk.LEFT, padx=(0, 12))

        self.quick_view_btn = tk.Button(
            action_bar,
            text="View Contacts",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            activebackground="#f1f5f9",
            relief=tk.SOLID,
            bd=1,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.quick_view_btn.pack(side=tk.LEFT)

    def create_summary_card(
        self, parent, icon, title, subtitle, bg_color, border_color, icon_color, row, col
    ):
        """Tạo từng thẻ thống kê màu sắc trên Dashboard."""
        card = tk.Frame(
            parent,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=20,
            pady=28,
            cursor="hand2",
        )
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        tk.Label(card, text=icon, font=("Arial", 22), bg=bg_color, fg=icon_color).pack(
            pady=(0, 8)
        )
        tk.Label(
            card, text=title, font=("Arial", 13, "bold"), bg=bg_color, fg="#0f172a"
        ).pack(pady=(0, 4))
        tk.Label(
            card, text=subtitle, font=("Arial", 10), bg=bg_color, fg="#64748b"
        ).pack()

        self.summary_cards[title] = card

    def handle_logout(self):
        """Đăng xuất tài khoản và quay về màn hình Login."""
        self.current_user = None
        self.current_role = None
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginAndDashboardUI(root)
    root.mainloop()