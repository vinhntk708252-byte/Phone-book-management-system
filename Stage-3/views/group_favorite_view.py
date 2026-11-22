# Phụ trách: Nguyễn Quốc Cường 

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class GroupFavoriteView:
    def __init__(self, app):
        self.app = app
        self.fav_kw = ""

    def _btn(self, parent, text, cmd, bg="#2563eb", fg="#ffffff", px=10, py=4, fsize=9):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            font=("Arial", fsize, "bold"), bd=0, padx=px, pady=py, cursor="hand2"
        )

    def render_favorites_screen(self):
        self.app.clear_content_area()
        hdr = tk.Frame(self.app.content_area, bg="#ffffff")
        hdr.pack(fill=tk.X, pady=(0, 16))
        tk.Label(hdr, text="☆ Favorite Contacts", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)

        s_ent = tk.Entry(hdr, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1, width=20)
        s_ent.pack(side=tk.RIGHT, ipady=3)
        s_ent.insert(0, self.fav_kw)
        self._btn(hdr, "🔍 Search", lambda: [setattr(self, "fav_kw", s_ent.get()), self.render_favorites_screen()], bg="#eff6ff", fg="#2563eb").pack(side=tk.RIGHT, padx=6)

        tbl = tk.Frame(self.app.content_area, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        tbl.pack(fill=tk.X)
        th = tk.Frame(tbl, bg="#f8fafc", pady=12, padx=20)
        th.pack(fill=tk.X)
        for i, h in enumerate(["Name", "Phone", "Group", "Action"]):
            th.columnconfigure(i, weight=1, uniform="f")
            tk.Label(th, text=h, font=("Arial", 10, "bold"), bg="#f8fafc", fg="#64748b", anchor="w").grid(row=0, column=i, sticky="ew")

        favs = self.app.contact_service.get_favorites_for_ui(self.app.current_user_id, self.fav_kw)
        if not favs:
            tk.Label(tbl, text="No favorite contacts yet.", font=("Arial", 11), bg="#ffffff", fg="#64748b", pady=24).pack(fill=tk.X)
        for c in favs:
            tk.Frame(tbl, bg="#f1f5f9", height=1).pack(fill=tk.X)
            rf = tk.Frame(tbl, bg="#ffffff", pady=12, padx=20)
            rf.pack(fill=tk.X)
            for i in range(4):
                rf.columnconfigure(i, weight=1, uniform="f")
            tk.Label(rf, text=c["name"], font=("Arial", 10, "bold"), bg="#ffffff", anchor="w").grid(row=0, column=0, sticky="ew")
            tk.Label(rf, text=c["phone"], font=("Arial", 10), bg="#ffffff", fg="#64748b", anchor="w").grid(row=0, column=1, sticky="ew")
            tk.Label(rf, text=c["group"], font=("Arial", 10), bg="#ffffff", fg="#2563eb", anchor="w").grid(row=0, column=2, sticky="ew")
            self._btn(rf, "★ Remove", lambda x=c: [self.app.contact_service.toggle_favorite(x), self.render_favorites_screen()], bg="#fefce8", fg="#d97706", px=8, py=3).grid(row=0, column=3, sticky="w")

    def render_groups_screen(self):
        self.app.clear_content_area()
        hdr = tk.Frame(self.app.content_area, bg="#ffffff")
        hdr.pack(fill=tk.X, pady=(0, 16))
        tk.Label(hdr, text="📁 Manage Groups", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)
        self._btn(hdr, "+   Add Group", self._add_grp, px=16, py=8, fsize=10).pack(side=tk.RIGHT)

        box = tk.Frame(self.app.content_area, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=18, pady=18)
        box.pack(fill=tk.X)
        grps = self.app.group_service.get_groups_for_ui(self.app.current_user_id)
        if not grps:
            tk.Label(box, text="No groups created yet. Click '+ Add Group' to start.", font=("Arial", 11), bg="#ffffff", fg="#64748b", pady=18).pack(fill=tk.X)
        for idx, g in enumerate(grps):
            row = tk.Frame(box, bg="#f8fafc", padx=18, pady=12)
            row.pack(fill=tk.X, pady=(0 if idx == 0 else 8, 0))
            tk.Label(row, text=g["name"], font=("Arial", 12, "bold"), bg="#f8fafc", fg="#0f172a").pack(side=tk.LEFT)
            self._btn(row, "🗑", lambda x=g: self._del_grp(x), bg="#fef2f2", fg="#ef4444", px=8, py=3).pack(side=tk.RIGHT, padx=3)
            self._btn(row, "✎", lambda x=g: self._ren_grp(x), bg="#eff6ff", fg="#2563eb", px=8, py=3).pack(side=tk.RIGHT, padx=3)
            self._btn(row, "👥 Members", lambda x=g: self._members_modal(x), bg="#f0fdf4", fg="#15803d", px=10, py=3).pack(side=tk.RIGHT, padx=6)
            tk.Label(row, text=f"{g['count']} contacts", font=("Arial", 10, "bold"), bg="#dbeafe", fg="#2563eb", padx=10, pady=3).pack(side=tk.RIGHT, padx=6)

    def _add_grp(self):
        name = simpledialog.askstring("Add Group", "Enter group name:", parent=self.app.root)
        if name is not None:
            ok, msg = self.app.group_service.create_group(self.app.current_user_id, name)
            messagebox.showinfo("Group", msg) if ok else messagebox.showerror("Error", msg)
            self.render_groups_screen()

    def _ren_grp(self, g):
        name = simpledialog.askstring("Rename Group", "New group name:", initialvalue=g["name"], parent=self.app.root)
        if name and name.strip() != g["name"]:
            ok, msg = self.app.group_service.rename_group(self.app.current_user_id, g["id"], g["name"], name)
            messagebox.showinfo("Group", msg) if ok else messagebox.showerror("Error", msg)
            self.render_groups_screen()

    def _del_grp(self, g):
        if messagebox.askyesno("Confirm Delete", f"Delete group '{g['name']}'?"):
            self.app.group_service.delete_group(self.app.current_user_id, g["id"], g["name"])
            self.render_groups_screen()

    def _members_modal(self, g):
        m = tk.Toplevel(self.app.root)
        m.title(f"Members - {g['name']}")
        m.geometry("540x400")
        m.configure(bg="#ffffff")
        m.transient(self.app.root)
        m.grab_set()

        top = tk.Frame(m, bg="#f8fafc", padx=14, pady=10)
        top.pack(fill=tk.X, padx=18, pady=14)
        contacts = self.app.contact_service.get_contacts_for_ui(self.app.current_user_id)
        opts = [f"{c['id']} - {c['name']}" for c in contacts]
        c_var = tk.StringVar(value=opts[0] if opts else "")
        ttk.Combobox(top, textvariable=c_var, values=opts, state="readonly", width=22).pack(side=tk.LEFT, padx=(0, 6))
        nick_e = tk.Entry(top, width=14, relief=tk.SOLID, bd=1)
        nick_e.pack(side=tk.LEFT, ipady=3, padx=(0, 6))
        nick_e.insert(0, "Nickname")

        lst = tk.Frame(m, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        lst.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

        def refresh():
            for w in lst.winfo_children():
                w.destroy()
            for mem in self.app.group_service.get_group_members(self.app.current_user_id, g["id"], g["name"]):
                r = tk.Frame(lst, bg="#ffffff", padx=12, pady=8)
                r.pack(fill=tk.X)
                tk.Label(r, text=f"{mem['fullName']} ({mem['phoneNumber']}) - Nickname: {mem['nickname'] or '—'}", font=("Arial", 10), bg="#ffffff").pack(side=tk.LEFT)
                self._btn(r, "✖", lambda cid=mem["contactID"]: [self.app.group_service.remove_contact_from_group(g["id"], cid), refresh(), self.render_groups_screen()], bg="#fef2f2", fg="#ef4444", px=6, py=2).pack(side=tk.RIGHT)

        def assign():
            if c_var.get():
                cid = c_var.get().split(" - ")[0]
                self.app.group_service.assign_contact_to_group(g["id"], g["name"], cid, "Member", nick_e.get())
                refresh()
                self.render_groups_screen()

        self._btn(top, "+ Assign", assign).pack(side=tk.LEFT)
        refresh()
