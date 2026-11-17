#login_dashboard.py Dang Truong Hiep
import tkinter as tk
from tkinter import messagebox, ttk

class LoginDashboardView:
    def __init__(self, app):
        self.app = app
        self.admin_kw = ""

    def _btn(self, parent, text, cmd, bg="#2563eb", fg="#ffffff", px=14, py=7, font_size=10):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            font=("Arial", font_size, "bold"), bd=0, padx=px, pady=py, cursor="hand2"
        )

    # LOGIN SCREEN (UC-01)
    def render_login_screen(self):
        self.app.clear_window()
        self.app.current_screen = "Login"
        self.app.main_container.config(bg="#e0f2fe")

        card = tk.Frame(self.app.main_container, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=410, height=500)

        tk.Label(card, text="📇", font=("Arial", 28), bg="#eff6ff", fg="#2563eb", padx=12, pady=6).pack(pady=(26, 8))
        tk.Label(card, text="Phone Book Management", font=("Arial", 17, "bold"), bg="#ffffff", fg="#0f172a").pack()
        tk.Label(card, text="Sign in to access your phone book", font=("Arial", 10), bg="#ffffff", fg="#64748b").pack(pady=(2, 12))

        self.err_box = tk.Frame(card, bg="#fef2f2", highlightbackground="#fecaca", highlightthickness=1)
        self.err_lbl = tk.Label(self.err_box, text="", font=("Arial", 10), bg="#fef2f2", fg="#dc2626", padx=12, pady=6)
        self.err_lbl.pack(anchor="w")

        form = tk.Frame(card, bg="#ffffff")
        form.pack(fill=tk.X, padx=35, pady=5)

        tk.Label(form, text="Username", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(4, 3))
        self.u_ent = tk.Entry(form, font=("Arial", 11), bg="#f8fafc", relief=tk.SOLID, bd=1)
        self.u_ent.pack(fill=tk.X, ipady=6, pady=(0, 12))
        self.u_ent.insert(0, "admin")

        tk.Label(form, text="Password", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(0, 3))
        self.p_ent = tk.Entry(form, font=("Arial", 11), bg="#f8fafc", show="•", relief=tk.SOLID, bd=1)
        self.p_ent.pack(fill=tk.X, ipady=6, pady=(0, 18))
        self.p_ent.insert(0, "123456")

        self._btn(form, "Login", self.handle_login, py=9, font_size=11).pack(fill=tk.X, pady=(0, 10))
        tk.Button(
            form, text="Create Account", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155",
            relief=tk.SOLID, bd=1, cursor="hand2", command=lambda: self.open_account_modal(False)
        ).pack(fill=tk.X, ipady=7)
        self.app.root.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self):
        ok, msg, user = self.app.auth_service.login(self.u_ent.get().strip(), self.p_ent.get().strip())
        if ok:
            self.app.current_user_id, self.app.current_user, self.app.current_role = user["userID"], user["username"], user["role"]
            self.app.root.unbind("<Return>")
            self.render_main_layout()
        else:
            self.err_lbl.config(text=f"ⓘ  {msg}")
            self.err_box.pack(fill=tk.X, padx=35, pady=(0, 8), before=self.u_ent.master)

    def open_account_modal(self, is_admin=False, edit_user=None):
        m = tk.Toplevel(self.app.root)
        m.title("Edit User" if edit_user else "Create Account")
        m.geometry("360x330" if (is_admin or edit_user) else "360x270")
        m.configure(bg="#ffffff")
        m.transient(self.app.root)
        m.grab_set()

        tk.Label(m, text="Modify Account" if edit_user else "Create Account", font=("Arial", 15, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor="w", padx=25, pady=(18, 10))
        f = tk.Frame(m, bg="#ffffff")
        f.pack(fill=tk.BOTH, expand=True, padx=25)

        tk.Label(f, text="Username *", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
        u_e = tk.Entry(f, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        u_e.pack(fill=tk.X, ipady=5, pady=(3, 10))
        if edit_user:
            u_e.insert(0, edit_user["username"])
            u_e.config(state="disabled")

        tk.Label(f, text="Password *", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
        p_e = tk.Entry(f, font=("Arial", 10), bg="#f8fafc", show="•", relief=tk.SOLID, bd=1)
        p_e.pack(fill=tk.X, ipady=5, pady=(3, 10))
        if edit_user:
            p_e.insert(0, edit_user.get("passwordHash", ""))

        r_var = tk.StringVar(value=edit_user["role"] if edit_user else "User")
        if is_admin or edit_user:
            tk.Label(f, text="Role", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
            ttk.Combobox(f, textvariable=r_var, values=["User", "Administrator"], state="readonly").pack(fill=tk.X, ipady=3, pady=(3, 12))

        def save():
            if edit_user:
                ok, msg = self.app.admin_service.update_user_account(edit_user, p_e.get().strip(), r_var.get(), self.app.current_user)
            else:
                ok, msg = self.app.auth_service.register_account(u_e.get().strip(), p_e.get().strip(), r_var.get())
            if ok:
                messagebox.showinfo("Success", msg, parent=m)
                m.destroy()
                if self.app.current_screen == "Admin":
                    self.app.switch_screen("Admin")
            else:
                messagebox.showerror("Error", msg, parent=m)

        self._btn(f, "Save", save).pack(fill=tk.X, pady=(6, 0))

    # SIDEBAR & SHELL
    def render_main_layout(self):
        self.app.clear_window()
        self.app.main_container.config(bg="#ffffff")

        sb = tk.Frame(self.app.main_container, bg="#0f172a", width=230)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        brand = tk.Frame(sb, bg="#0f172a", pady=22)
        brand.pack(fill=tk.X, padx=18)
        tk.Label(brand, text="📇 Phone Book", font=("Arial", 14, "bold"), bg="#0f172a", fg="#ffffff", anchor="w").pack(fill=tk.X)
        tk.Label(brand, text="Management System", font=("Arial", 9), bg="#0f172a", fg="#94a3b8", anchor="w").pack(fill=tk.X)

        nav = tk.Frame(sb, bg="#0f172a")
        nav.pack(fill=tk.X, padx=12, pady=8)
        self.app.nav_buttons = {}
        for txt, key in [("🏠   Home", "Home"), ("👥   Contacts", "Contacts"), ("⭐   Favorites", "Favorites"), ("📁   Groups", "Groups"), ("⚙️   Admin", "Admin")]:
            b = tk.Button(
                nav, text=txt, font=("Arial", 11), bg="#0f172a", fg="#cbd5e1",
                bd=0, anchor="w", padx=14, pady=9, cursor="hand2", command=lambda k=key: self.app.switch_screen(k)
            )
            b.pack(fill=tk.X, pady=2)
            self.app.nav_buttons[key] = b

        foot = tk.Frame(sb, bg="#0f172a", pady=14)
        foot.pack(side=tk.BOTTOM, fill=tk.X, padx=14)
        tk.Button(foot, text="↪   Logout", font=("Arial", 11), bg="#0f172a", fg="#cbd5e1", bd=0, anchor="w", padx=10, pady=6, cursor="hand2", command=self.app.handle_logout).pack(fill=tk.X)
        tk.Frame(foot, bg="#1e293b", height=1).pack(fill=tk.X, pady=8)
        u_box = tk.Frame(foot, bg="#0f172a")
        u_box.pack(fill=tk.X)
        tk.Label(u_box, text="👤", font=("Arial", 14), bg="#2563eb", fg="#ffffff", padx=7, pady=3).pack(side=tk.LEFT, padx=(4, 8))
        u_txt = tk.Frame(u_box, bg="#0f172a")
        u_txt.pack(side=tk.LEFT)
        tk.Label(u_txt, text=self.app.current_user, font=("Arial", 10, "bold"), bg="#0f172a", fg="#ffffff", anchor="w").pack(fill=tk.X)
        tk.Label(u_txt, text=self.app.current_role, font=("Arial", 8), bg="#0f172a", fg="#94a3b8", anchor="w").pack(fill=tk.X)

        self.app.content_area = tk.Frame(self.app.main_container, bg="#ffffff")
        self.app.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=32, pady=26)
        self.app.switch_screen("Home")

    # HOME DASHBOARD
    def render_dashboard_content(self):
        tk.Label(self.app.content_area, text="Dashboard", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor="w", pady=(0, 18))

        grid = tk.Frame(self.app.content_area, bg="#ffffff")
        grid.pack(fill=tk.X, pady=(0, 18))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        c_cnt = len(self.app.contact_service.get_contacts_for_ui(self.app.current_user_id))
        f_cnt = len(self.app.contact_service.get_favorites_for_ui(self.app.current_user_id))
        g_cnt = len(self.app.group_service.get_groups_for_ui(self.app.current_user_id))

        cards = [
            ("👥", "My Contacts", f"{c_cnt} contacts", "#eff6ff", "#bfdbfe", "#2563eb", 0, 0, lambda: self.app.switch_screen("Contacts")),
            ("⭐", "Favorites", f"{f_cnt} contacts", "#fefce8", "#fef08a", "#eab308", 0, 1, lambda: self.app.switch_screen("Favorites")),
            ("📁", "Groups", f"{g_cnt} groups", "#f0fdf4", "#bbf7d0", "#16a34a", 1, 0, lambda: self.app.switch_screen("Groups")),
            ("⊕", "Add Contact", "Create new", "#faf5ff", "#e9d5ff", "#9333ea", 1, 1, self.app.contact_group_view.open_add_contact_modal),
        ]
        for ic, t, sub, bg, bd_c, ic_c, r, c, cmd in cards:
            box = tk.Frame(grid, bg=bg, highlightbackground=bd_c, highlightthickness=1, padx=18, pady=22, cursor="hand2")
            box.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            w1 = tk.Label(box, text=ic, font=("Arial", 20), bg=bg, fg=ic_c)
            w2 = tk.Label(box, text=t, font=("Arial", 13, "bold"), bg=bg, fg="#0f172a")
            w3 = tk.Label(box, text=sub, font=("Arial", 10), bg=bg, fg="#64748b")
            w1.pack(pady=(0, 6)); w2.pack(pady=(0, 2)); w3.pack()
            for w in (box, w1, w2, w3):
                w.bind("<Button-1>", lambda e, fn=cmd: fn())

        bar = tk.Frame(self.app.content_area, bg="#f8fafc", highlightbackground="#e2e8f0", highlightthickness=1, padx=18, pady=14)
        bar.pack(fill=tk.X)
        self._btn(bar, "+   Add Contact", self.app.contact_group_view.open_add_contact_modal).pack(side=tk.LEFT, padx=(0, 10))
        self._btn(bar, "View Contacts", lambda: self.app.switch_screen("Contacts"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)

    # ADMIN DASHBOARD (UC-09, UC-10, UC-11, UC-12)
    def render_admin_screen(self):
        hdr = tk.Frame(self.app.content_area, bg="#ffffff")
        hdr.pack(fill=tk.X, pady=(0, 14))
        tk.Label(hdr, text="⚙️ Admin Dashboard", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)

        if self.app.current_role != "Administrator":
            tk.Label(
                self.app.content_area, text="🔒 Access Denied: Administrators only.",
                font=("Arial", 11, "bold"), bg="#fef2f2", fg="#dc2626", padx=20, pady=20
            ).pack(fill=tk.X)
            return

        self._btn(hdr, "+ Add Account", lambda: self.open_account_modal(True)).pack(side=tk.RIGHT)

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

        tb = tk.Frame(self.app.content_area, bg="#ffffff")
        tb.pack(fill=tk.X, pady=(0, 8))
        tk.Label(tb, text="User Account Management", font=("Arial", 13, "bold"), bg="#ffffff").pack(side=tk.LEFT)
        s_ent = tk.Entry(tb, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1, width=20)
        s_ent.pack(side=tk.RIGHT, ipady=3)
        s_ent.insert(0, self.admin_kw)
        self._btn(tb, "🔍 Search", lambda: [setattr(self, "admin_kw", s_ent.get()), self.render_admin_screen()], bg="#eff6ff", fg="#2563eb", px=10, py=4, font_size=9).pack(side=tk.RIGHT, padx=6)

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
            self._btn(ac, "🔑 Edit", lambda usr=u: self.open_account_modal(True, usr), bg="#f1f5f9", fg="#334155", px=8, py=3, font_size=9).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🔄 Role", lambda usr=u: self._adm_act(self.app.admin_service.toggle_user_role, usr), bg="#eff6ff", fg="#2563eb", px=8, py=3, font_size=9).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🔒 Lock" if act else "🔓 Unlock", lambda usr=u: self._adm_act(self.app.admin_service.toggle_user_lock, usr), bg="#fefce8", fg="#d97706", px=8, py=3, font_size=9).pack(side=tk.LEFT, padx=2)
            self._btn(ac, "🗑", lambda usr=u: self._adm_del(usr), bg="#fef2f2", fg="#ef4444", px=8, py=3, font_size=9).pack(side=tk.LEFT, padx=2)

    def _adm_act(self, fn, user):
        ok, msg = fn(user, self.app.current_user)
        messagebox.showinfo("Admin", msg) if ok else messagebox.showwarning("Restricted", msg)
        self.render_admin_screen()

    def _adm_del(self, user):
        if messagebox.askyesno("Confirm Delete", f"Delete user '{user['username']}'?"):
            self._adm_act(self.app.admin_service.delete_user, user)
