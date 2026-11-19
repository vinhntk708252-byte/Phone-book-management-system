# File: views/admin_view.py
# Phụ trách: Vũ Trung Tiến (Cặp B)
# Nhiệm vụ: Giao diện Admin Dashboard (UC-09 Quản lý User, UC-10 Khóa/Mở, UC-11 Phân quyền, UC-12 Thống kê)

import tkinter as tk
from tkinter import messagebox


class AdminView:
    def __init__(self, app):
        self.app = app
        self.admin_kw = ""

    def _btn(self, parent, text, cmd, bg="#2563eb", fg="#ffffff", px=10, py=4, fsize=9):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            font=("Arial", fsize, "bold"), bd=0, padx=px, pady=py, cursor="hand2"
        )

    def render_admin_screen(self):
        hdr = tk.Frame(self.app.content_area, bg="#ffffff")
        hdr.pack(fill=tk.X, pady=(0, 14))
        tk.Label(hdr, text="⚙️ Admin Dashboard", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)

        if not self.app.session.is_admin():
            tk.Label(
                self.app.content_area, text="🔒 Access Denied: Only Administrators can access this section.",
                font=("Arial", 11, "bold"), bg="#fef2f2", fg="#dc2626", padx=20, pady=20
            ).pack(fill=tk.X)
            return

        self._btn(hdr, "+ Add Account", lambda: self.app.login_dashboard_view.open_account_modal(True), px=14, py=7, fsize=10).pack(side=tk.RIGHT)

        # UC-12: System Statistics
        st = self.app.admin_service.get_system_statistics()
        s_box = tk.Frame(self.app.content_area, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=16, pady=12)
        s_box.pack(fill=tk.X, pady=(0, 14))

        for lbl, val, fg in [
            ("Total System Users", f"{st['total_users']} accounts ({st['active_users']} active, {st['locked_users']} locked) | Contacts: {st['total_contacts']} | Groups: {st['total_groups']}", "#2563eb"),
            ("Database Storage", st["storage_type"], "#15803d"),
        ]:
            r = tk.Frame(s_box, bg="#f8fafc", padx=14, pady=10)
            r.pack(fill=tk.X, pady=3)
            tk.Label(r, text=lbl, font=("Arial", 11, "bold"), bg="#f8fafc", fg="#0f172a").pack(side=tk.LEFT)
            tk.Label(r, text=val, font=("Arial", 11, "bold"), bg="#f8fafc", fg=fg).pack(side=tk.RIGHT)

        # UC-09, UC-10, UC-11: User Account Management Table
        tb = tk.Frame(self.app.content_area, bg="#ffffff")
        tb.pack(fill=tk.X, pady=(0, 8))
        tk.Label(tb, text="User Account Management", font=("Arial", 13, "bold"), bg="#ffffff").pack(side=tk.LEFT)
        s_ent = tk.Entry(tb, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1, width=20)
        s_ent.pack(side=tk.RIGHT, ipady=3)
        s_ent.insert(0, self.admin_kw)
        self._btn(tb, "🔍 Search", lambda: [setattr(self, "admin_kw", s_ent.get()), self.render_admin_screen()], bg="#eff6ff", fg="#2563eb").pack(side=tk.RIGHT, padx=6)

        tbl = tk.Frame(self.app.content_area, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        tbl.pack(fill=tk.X)
        th = tk.Frame(tbl, bg="#f8fafc", pady=10, padx=16)
        th.pack(fill=tk.X)
        for i, h in enumerate(["Username", "Role", "Status", "Actions"]):
            th.columnconfigure(i, weight=3 if i == 3 else 2, uniform="adm")
            tk.Label(th, text=h, font=("Arial", 10, "bold"), bg="#f8fafc", fg="#64748b", anchor="w").grid(row=0, column=i, sticky="ew")

        for u in self.app.admin_service.get_all_users(self.admin_kw):
            tk.Frame(tbl, bg="#f1f5f9", height=1).pack(fill=tk.X)
            rf = tk.Frame(tbl, bg="#ffffff", pady=9, padx=16)
            rf.pack(fill=tk.X)
            for i in range(4):
                rf.columnconfigure(i, weight=3 if i == 3 else 2, uniform="adm")
            act = int(u.get("isActive", 1)) == 1
            tk.Label(rf, text=u["username"], font=("Arial", 10, "bold"), bg="#ffffff", anchor="w").grid(row=0, column=0, sticky="ew")
            tk.Label(rf, text=u["role"], font=("Arial", 10), bg="#ffffff", fg="#2563eb" if u["role"] == "Administrator" else "#475569", anchor="w").grid(row=0, column=1, sticky="ew")
            tk.Label(rf, text="Active" if act else "Locked", font=("Arial", 10, "bold"), bg="#ffffff", fg="#16a34a" if act else "#dc2626", anchor="w").grid(row=0, column=2, sticky="ew")

            ac = tk.Frame(rf, bg="#ffffff")
            ac.grid(row=0, column=3, sticky="w")
            self._btn(ac, "🔑 Edit", lambda usr=u: self.app.login_dashboard_view.open_account_modal(True, usr), bg="#f1f5f9", fg="#334155", px=8, py=3).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🔄 Role", lambda usr=u: self._adm_act(self.app.admin_service.toggle_user_role, usr), bg="#eff6ff", fg="#2563eb", px=8, py=3).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🔒 Lock" if act else "🔓 Unlock", lambda usr=u: self._adm_act(self.app.admin_service.toggle_user_lock, usr), bg="#fefce8", fg="#d97706", px=8, py=3).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🗑", lambda usr=u: self._adm_del(usr), bg="#fef2f2", fg="#ef4444", px=8, py=3).pack(side=tk.LEFT, padx=2)

    def _adm_act(self, fn, user):
        ok, msg = fn(user, self.app.current_user)
        messagebox.showinfo("Admin", msg) if ok else messagebox.showwarning("Restricted", msg)
        self.render_admin_screen()

    def _adm_del(self, user):
        if messagebox.askyesno("Confirm Delete", f"Delete user '{user['username']}'?"):
            self._adm_act(self.app.admin_service.delete_user, user)
