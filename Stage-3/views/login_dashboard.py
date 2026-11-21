# Phụ trách: Đặng Trường Hiệp 

import tkinter as tk
from tkinter import messagebox, ttk

class LoginDashboardView:
    def __init__(self, app):
        self.app = app

    def _btn(self, parent, text, cmd, bg="#2563eb", fg="#ffffff", px=14, py=7, font_size=10):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            font=("Arial", font_size, "bold"), bd=0, padx=px, pady=py, cursor="hand2"
        )

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
            self.app.session.start_session(user)
            self.app.current_user_id = user["userID"]
            self.app.current_user = user["username"]
            self.app.current_role = user["role"]
            self.app.root.unbind("<Return>")
            self.app.render_main_layout()
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
            ("⊕", "Add Contact", "Create new", "#faf5ff", "#e9d5ff", "#9333ea", 1, 1, self.app.contact_view.open_add_contact_modal),
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
        self._btn(bar, "+   Add Contact", self.app.contact_view.open_add_contact_modal).pack(side=tk.LEFT, padx=(0, 10))
        self._btn(bar, "View Contacts", lambda: self.app.switch_screen("Contacts"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)
