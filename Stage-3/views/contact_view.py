# Phụ trách: Bùi Lê Giang 

import tkinter as tk
from tkinter import messagebox, ttk

class ContactView:
    def __init__(self, app):
        self.app = app
        self.kw = ""
        self.grp_filter = "All"
        self.sort_by = "name"
        self.sort_asc = True
        self.page = 1

    def _btn(self, parent, text, cmd, bg="#2563eb", fg="#ffffff", px=12, py=5, fsize=9):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=("Arial", fsize, "bold"), bd=0, padx=px, pady=py, cursor="hand2")

    def render_contacts_screen(self):
        hdr = tk.Frame(self.app.content_area, bg="#ffffff")
        hdr.pack(fill=tk.X, pady=(0, 12))
        tk.Label(hdr, text="Contacts", font=("Arial", 22, "bold"), bg="#ffffff", fg="#0f172a").pack(side=tk.LEFT)
        self._btn(hdr, "+   Add Contact", self.open_add_contact_modal, px=16, py=8, fsize=10).pack(side=tk.RIGHT)

        bar = tk.Frame(self.app.content_area, bg="#f8fafc", highlightbackground="#e2e8f0", highlightthickness=1, padx=12, pady=8)
        bar.pack(fill=tk.X, pady=(0, 12))

        s_ent = tk.Entry(bar, font=("Arial", 10), width=22, relief=tk.SOLID, bd=1)
        s_ent.pack(side=tk.LEFT, ipady=4, padx=(0, 6))
        s_ent.insert(0, self.kw)

        grps = ["All", "Unassigned"] + [g["name"] for g in self.app.group_service.get_groups_for_ui(self.app.current_user_id)]
        g_var = tk.StringVar(value=self.grp_filter if self.grp_filter in grps else "All")
        ttk.Combobox(bar, textvariable=g_var, values=grps, state="readonly", width=12).pack(side=tk.LEFT, ipady=2, padx=(0, 6))

        def do_search():
            self.kw, self.grp_filter, self.page = s_ent.get().strip(), g_var.get(), 1
            self.app.switch_screen("Contacts")

        s_ent.bind("<Return>", lambda e: do_search())
        self._btn(bar, "🔍 Search", do_search).pack(side=tk.LEFT, padx=(0, 4))
        self._btn(bar, "↺ Reset", lambda: [setattr(self, "kw", ""), setattr(self, "grp_filter", "All"), setattr(self, "page", 1), self.app.switch_screen("Contacts")], bg="#e2e8f0", fg="#334155").pack(side=tk.LEFT)
        self._btn(bar, f"⇅ Sort: {'Name' if self.sort_by=='name' else 'Phone'} ({'ASC' if self.sort_asc else 'DESC'})", self._toggle_sort, bg="#eff6ff", fg="#2563eb").pack(side=tk.RIGHT)

        tbl = tk.Frame(self.app.content_area, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        tbl.pack(fill=tk.X)
        th = tk.Frame(tbl, bg="#f8fafc", pady=12, padx=18)
        th.pack(fill=tk.X)
        for i, h in enumerate(["Name", "Phone", "Email / Note", "Group", "Action"]):
            th.columnconfigure(i, weight=3 if i in (0, 4) else 2, uniform="c")
            tk.Label(th, text=h, font=("Arial", 10, "bold"), bg="#f8fafc", fg="#64748b", anchor="w").grid(row=0, column=i, sticky="ew")

        items = self.app.contact_service.search_contacts(self.kw, self.app.current_user_id, self.grp_filter)
        items = self.app.contact_service.sort_contacts(items, self.sort_by, self.sort_asc)
        page_items, self.page, total_pages = self.app.contact_service.paginate_contacts(items, self.page, 5)

        if not page_items:
            tk.Label(tbl, text="No contacts found." if self.kw or self.grp_filter != "All" else "No contacts available.", font=("Arial", 11), bg="#ffffff", fg="#64748b", pady=26).pack(fill=tk.X)
        else:
            for c in page_items:
                tk.Frame(tbl, bg="#f1f5f9", height=1).pack(fill=tk.X)
                rf = tk.Frame(tbl, bg="#ffffff", pady=10, padx=18)
                rf.pack(fill=tk.X)
                for i in range(5):
                    rf.columnconfigure(i, weight=3 if i in (0, 4) else 2, uniform="c")

                tk.Label(rf, text=c["name"], font=("Arial", 10, "bold"), bg="#ffffff", anchor="w").grid(row=0, column=0, sticky="ew")
                tk.Label(rf, text=c["phone"], font=("Arial", 10), bg="#ffffff", fg="#475569", anchor="w").grid(row=0, column=1, sticky="ew")
                tk.Label(rf, text=c["email"] or c["note"] or "—", font=("Arial", 9), bg="#ffffff", fg="#64748b", anchor="w").grid(row=0, column=2, sticky="ew")
                tk.Label(rf, text=c["group"], font=("Arial", 9, "bold"), bg="#ffffff", fg="#2563eb", anchor="w").grid(row=0, column=3, sticky="ew")

                ac = tk.Frame(rf, bg="#ffffff")
                ac.grid(row=0, column=4, sticky="w")
                fav = c.get("favorite", False)
                self._btn(ac, "👁", lambda x=c: self.show_details(x), bg="#f1f5f9", fg="#0f172a", px=8, py=3).pack(side=tk.LEFT, padx=2)
                self._btn(ac, "★" if fav else "☆", lambda x=c: [self.app.contact_service.toggle_favorite(x), self.app.switch_screen("Contacts")], bg="#fefce8" if fav else "#f8fafc", fg="#eab308" if fav else "#94a3b8", px=8, py=3).pack(side=tk.LEFT, padx=2)
                self._btn(ac, "✎", lambda x=c: self._contact_modal("Edit Contact", x), bg="#eff6ff", fg="#2563eb", px=8, py=3).pack(side=tk.LEFT, padx=2)
                self._btn(ac, "🗑", lambda x=c: self.delete_contact(x), bg="#fef2f2", fg="#ef4444", px=8, py=3).pack(side=tk.LEFT, padx=2)

        pager = tk.Frame(self.app.content_area, bg="#ffffff")
        pager.pack(fill=tk.X, pady=(10, 0))
        tk.Label(pager, text=f"Showing {len(page_items)} of {len(items)} contacts | Page {self.page}/{total_pages}", font=("Arial", 10, "bold"), bg="#ffffff", fg="#64748b").pack(side=tk.LEFT)
        self._btn(pager, "Next ▶", lambda: self._go_page(1, total_pages), bg="#f1f5f9", fg="#0f172a").pack(side=tk.RIGHT)
        self._btn(pager, "◀ Prev", lambda: self._go_page(-1, total_pages), bg="#f1f5f9", fg="#0f172a").pack(side=tk.RIGHT, padx=6)

    def _toggle_sort(self):
        if self.sort_by == "name" and self.sort_asc:
            self.sort_asc = False
        elif self.sort_by == "name":
            self.sort_by, self.sort_asc = "phone", True
        else:
            self.sort_by, self.sort_asc = "name", True
        self.app.switch_screen("Contacts")

    def _go_page(self, d, total):
        if 1 <= self.page + d <= total:
            self.page += d
            self.app.switch_screen("Contacts")

    def show_details(self, c):
        info = (
            f"ID: {c['id']}\n"
            f"Name: {c['name']}\n"
            f"Phone: {c['phone']}\n"
            f"Email: {c['email'] or 'N/A'}\n"
            f"Address: {c['address'] or 'N/A'}\n"
            f"Group: {c['group']}\n"
            f"Favorite: {'Yes' if c['favorite'] else 'No'}\n"
            f"Note: {c['note'] or 'None'}"
        )
        messagebox.showinfo("Contact Details", info)

    def open_add_contact_modal(self):
        self._contact_modal("Add Contact", None)

    def _contact_modal(self, title, c=None):
        m = tk.Toplevel(self.app.root)
        m.title(title)
        m.geometry("410x520")
        m.configure(bg="#ffffff")
        m.transient(self.app.root)
        m.grab_set()

        tk.Label(m, text=title, font=("Arial", 15, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor="w", padx=26, pady=(16, 8))
        f = tk.Frame(m, bg="#ffffff")
        f.pack(fill=tk.BOTH, expand=True, padx=26)

        ents = {}
        for lbl, key in [("Full Name *", "name"), ("Phone (10 digits) *", "phone"), ("Email", "email"), ("Address", "address"), ("Notes", "note")]:
            tk.Label(f, text=lbl, font=("Arial", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            e = tk.Entry(f, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
            e.pack(fill=tk.X, ipady=4, pady=(2, 7))
            if c:
                e.insert(0, c.get(key, ""))
            ents[key] = e

        tk.Label(f, text="Group", font=("Arial", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
        g_names = ["Unassigned"] + [g["name"] for g in self.app.group_service.get_groups_for_ui(self.app.current_user_id)]
        g_var = tk.StringVar(value=c["group"] if c else g_names[0])
        ttk.Combobox(f, textvariable=g_var, values=g_names).pack(fill=tk.X, ipady=3, pady=(2, 8))

        fav_var = tk.BooleanVar(value=c.get("favorite", False) if c else False)
        tk.Checkbutton(f, text="Mark as Favorite (⭐)", variable=fav_var, bg="#ffffff").pack(anchor="w", pady=(0, 10))

        def save():
            grp = g_var.get().strip() or "Unassigned"
            existing = [g["name"].lower() for g in self.app.group_service.get_groups_for_ui(self.app.current_user_id)]
            if grp != "Unassigned" and grp.lower() not in existing:
                self.app.group_service.create_group(self.app.current_user_id, grp)
            ok, msg = self.app.contact_service.validate_and_save(
                self.app.current_user_id, ents["name"].get().strip(), ents["phone"].get().strip(),
                grp, fav_var.get(), ents["email"].get().strip(), ents["address"].get().strip(),
                ents["note"].get().strip(), c["id"] if c else None
            )
            if not ok:
                messagebox.showerror("Error", msg, parent=m)
                return
            messagebox.showinfo("Success", msg, parent=m)
            m.destroy()
            self.app.switch_screen("Contacts")

        self._btn(f, "Save Contact", save, py=7, fsize=10).pack(fill=tk.X)

    def delete_contact(self, c):
        if messagebox.askyesno("Confirm Delete", f"Delete contact '{c['name']}'?"):
            self.app.contact_service.delete_contact(c["id"])
            self.app.switch_screen("Contacts")
