import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class PhoneBookApp:
    """Giao diện Phone Book Management System.
    Phần Contact và Group được triển khai ở mức giao diện + dữ liệu mẫu
    để thành viên phụ trách SQLite/DAO có thể tích hợp sau.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book Management System")
        self.root.geometry("1150x720")
        self.root.minsize(1000, 650)

        self.bg = "#f1f5f9"
        self.navy = "#0f172a"
        self.blue = "#2563eb"
        self.current_user = None
        self.current_role = None
        self.current_screen = None

        self.groups = ["Family", "Friends", "Colleagues"]
        self.contacts = [
            {"id": 1, "name": "Nguyễn Văn An", "phone": "0901234567",
             "email": "an@gmail.com", "address": "Cần Thơ", "group": "Family",
             "note": "Anh họ", "favorite": True},
            {"id": 2, "name": "Trần Thị Bình", "phone": "0912345678",
             "email": "binh@gmail.com", "address": "TP. Hồ Chí Minh", "group": "Friends",
             "note": "Bạn học", "favorite": False},
            {"id": 3, "name": "Lê Minh Khang", "phone": "0987654321",
             "email": "khang@gmail.com", "address": "Đồng Nai", "group": "Colleagues",
             "note": "Đồng nghiệp", "favorite": True},
        ]
        self.next_contact_id = 4
        self.page = 0
        self.page_size = 8
        self.sort_reverse = False

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure(
            "Treeview", rowheight=30, font=("Arial", 10),
            background="white", fieldbackground="white"
        )
        self.style.configure(
            "Treeview.Heading", font=("Arial", 10, "bold"),
            background="#e2e8f0", foreground=self.navy
        )

        self.container = tk.Frame(root, bg=self.bg)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.show_login()

    # -------------------- COMMON --------------------
    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def make_button(self, parent, text, command, color=None, width=None):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=color or self.blue, fg="white", activebackground="#1d4ed8",
            activeforeground="white", relief=tk.FLAT, bd=0,
            font=("Arial", 10, "bold"), padx=12, pady=8, cursor="hand2"
        )

    def show_login(self):
        self.clear()
        self.current_screen = "Login"
        self.container.configure(bg="#e0f2fe")

        card = tk.Frame(self.container, bg="white", padx=38, pady=30,
                        highlightbackground="#cbd5e1", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=430, height=460)

        tk.Label(card, text="📇", font=("Arial", 32), bg="white").pack(pady=(8, 5))
        tk.Label(card, text="Phone Book Management",
                 font=("Arial", 18, "bold"), bg="white", fg=self.navy).pack(pady=(0, 25))

        tk.Label(card, text="Username", bg="white", fg="#334155",
                 font=("Arial", 10, "bold"), anchor="w").pack(fill=tk.X)
        username = tk.Entry(card, font=("Arial", 11), relief=tk.SOLID, bd=1)
        username.pack(fill=tk.X, ipady=8, pady=(6, 18))
        username.insert(0, "admin")

        tk.Label(card, text="Password", bg="white", fg="#334155",
                 font=("Arial", 10, "bold"), anchor="w").pack(fill=tk.X)
        password = tk.Entry(card, font=("Arial", 11), show="•",
                             relief=tk.SOLID, bd=1)
        password.pack(fill=tk.X, ipady=8, pady=(6, 22))
        password.insert(0, "123456")

        def login():
            if username.get().strip() == "admin" and password.get().strip() == "123456":
                self.current_user = "admin"
                self.current_role = "Administrator"
                self.show_dashboard()
            else:
                messagebox.showerror("Login failed", "Invalid username or password.")

        self.make_button(card, "Login", login).pack(fill=tk.X, ipady=2)
        tk.Label(card, text="Demo account: admin / 123456",
                 bg="white", fg="#64748b", font=("Arial", 9)).pack(pady=14)
        password.bind("<Return>", lambda _event: login())

    def build_shell(self, active):
        self.clear()
        self.current_screen = active
        self.container.configure(bg="white")

        sidebar = tk.Frame(self.container, bg=self.navy, width=225)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📇 Phone Book", bg=self.navy, fg="white",
                 font=("Arial", 15, "bold"), anchor="w").pack(fill=tk.X, padx=20, pady=(28, 2))
        tk.Label(sidebar, text="Management System", bg=self.navy, fg="#94a3b8",
                 font=("Arial", 9), anchor="w").pack(fill=tk.X, padx=20, pady=(0, 25))

        items = [
            ("🏠  Dashboard", self.show_dashboard),
            ("👥  Contacts", self.show_contacts),
            ("⭐  Favorites", self.show_favorites),
            ("📁  Groups", self.show_groups),
        ]
        for label, action in items:
            btn = tk.Button(sidebar, text=label, command=action, anchor="w",
                            padx=18, pady=12, bd=0, relief=tk.FLAT,
                            bg=self.blue if active == label.split()[-1] else self.navy,
                            fg="white", activebackground="#1e293b",
                            activeforeground="white", font=("Arial", 10, "bold"),
                            cursor="hand2")
            btn.pack(fill=tk.X, padx=10, pady=3)

        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=15, pady=(25, 12))
        tk.Label(sidebar, text=f"👤  {self.current_user or 'admin'}",
                 bg=self.navy, fg="white", font=("Arial", 10, "bold"),
                 anchor="w").pack(fill=tk.X, padx=18, pady=5)
        tk.Label(sidebar, text=self.current_role or "Administrator",
                 bg=self.navy, fg="#94a3b8", font=("Arial", 9),
                 anchor="w").pack(fill=tk.X, padx=43)
        tk.Button(sidebar, text="↪  Logout", command=self.logout,
                  anchor="w", padx=18, pady=12, bd=0, bg=self.navy,
                  fg="#cbd5e1", activebackground="#1e293b",
                  activeforeground="white", cursor="hand2").pack(
                      side=tk.BOTTOM, fill=tk.X, padx=10, pady=18)

        self.content = tk.Frame(self.container, bg="#f8fafc")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def page_heading(self, title, subtitle=None):
        head = tk.Frame(self.content, bg="#f8fafc")
        head.pack(fill=tk.X, padx=30, pady=(25, 18))
        tk.Label(head, text=title, bg="#f8fafc", fg=self.navy,
                 font=("Arial", 22, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(head, text=subtitle, bg="#f8fafc", fg="#64748b",
                     font=("Arial", 10)).pack(anchor="w", pady=(5, 0))

    def logout(self):
        self.current_user = None
        self.current_role = None
        self.show_login()

    # -------------------- DASHBOARD --------------------
    def show_dashboard(self):
        self.build_shell("Dashboard")
        self.page_heading("Dashboard", "Overview of your personal phone book")
        stats = tk.Frame(self.content, bg="#f8fafc")
        stats.pack(fill=tk.X, padx=22)
        values = [
            ("👥", "My Contacts", len(self.contacts), "#eff6ff"),
            ("⭐", "Favorites", sum(c["favorite"] for c in self.contacts), "#fefce8"),
            ("📁", "Groups", len(self.groups), "#f0fdf4"),
        ]
        for i, (icon, label, value, color) in enumerate(values):
            card = tk.Frame(stats, bg=color, padx=20, pady=22,
                            highlightbackground="#e2e8f0", highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=8, pady=8)
            stats.columnconfigure(i, weight=1)
            tk.Label(card, text=icon, bg=color, font=("Arial", 22)).pack()
            tk.Label(card, text=str(value), bg=color, fg=self.navy,
                     font=("Arial", 20, "bold")).pack(pady=5)
            tk.Label(card, text=label, bg=color, fg="#475569",
                     font=("Arial", 10)).pack()
        actions = tk.Frame(self.content, bg="white", padx=20, pady=18)
        actions.pack(fill=tk.X, padx=30, pady=22)
        self.make_button(actions, "+ Add Contact", self.add_contact).pack(side=tk.LEFT, padx=5)
        self.make_button(actions, "View Contacts", self.show_contacts, "#475569").pack(side=tk.LEFT, padx=5)
        self.make_button(actions, "Manage Groups", self.show_groups, "#475569").pack(side=tk.LEFT, padx=5)

    # -------------------- CONTACT MANAGEMENT --------------------
    def show_contacts(self, filtered=None, title="Contact Management"):
        self.build_shell("Contacts")
        self.page_heading(title, "View, search, add, update and delete contact information")

        toolbar = tk.Frame(self.content, bg="#f8fafc")
        toolbar.pack(fill=tk.X, padx=30, pady=(0, 12))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(toolbar, textvariable=self.search_var,
                                font=("Arial", 10), width=28, relief=tk.SOLID, bd=1)
        search_entry.pack(side=tk.LEFT, ipady=7, padx=(0, 8))
        search_entry.insert(0, "")
        search_entry.bind("<KeyRelease>", lambda _e: self.refresh_contacts())

        tk.Label(toolbar, text="Search by name or phone", bg="#f8fafc",
                 fg="#64748b", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 15))
        self.make_button(toolbar, "+ Add Contact", self.add_contact).pack(side=tk.RIGHT, padx=4)
        self.make_button(toolbar, "Edit", self.edit_contact, "#0f766e").pack(side=tk.RIGHT, padx=4)
        self.make_button(toolbar, "Delete", self.delete_contact, "#dc2626").pack(side=tk.RIGHT, padx=4)

        table_frame = tk.Frame(self.content, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))
        columns = ("name", "phone", "email", "group", "favorite")
        self.contact_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         selectmode="browse")
        headings = {
            "name": ("Full Name", 190), "phone": ("Phone Number", 130),
            "email": ("Email", 190), "group": ("Group", 130),
            "favorite": ("Favorite", 90)
        }
        for col, (text, width) in headings.items():
            self.contact_tree.heading(col, text=text,
                                      command=lambda c=col: self.sort_contacts(c))
            self.contact_tree.column(col, width=width, anchor=tk.W)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                  command=self.contact_tree.yview)
        self.contact_tree.configure(yscrollcommand=scrollbar.set)
        self.contact_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contact_tree.bind("<Double-1>", lambda _e: self.view_contact())

        bottom = tk.Frame(self.content, bg="#f8fafc")
        bottom.pack(fill=tk.X, padx=30, pady=(0, 22))
        self.page_label = tk.Label(bottom, text="", bg="#f8fafc", fg="#475569")
        self.page_label.pack(side=tk.LEFT)
        self.make_button(bottom, "Next ▶", self.next_page, "#475569").pack(side=tk.RIGHT, padx=4)
        self.make_button(bottom, "◀ Previous", self.previous_page, "#475569").pack(side=tk.RIGHT, padx=4)
        self.refresh_contacts(filtered)

    def refresh_contacts(self, filtered=None):
        if not hasattr(self, "contact_tree") or not self.contact_tree.winfo_exists():
            return
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        data = filtered if filtered is not None else self.contacts
        if query:
            data = [c for c in data if query in c["name"].lower() or query in c["phone"].lower()]
        self.visible_contacts = data
        total_pages = max(1, (len(data) + self.page_size - 1) // self.page_size)
        self.page = min(self.page, total_pages - 1)
        start = self.page * self.page_size
        shown = data[start:start + self.page_size]

        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
        for contact in shown:
            self.contact_tree.insert(
                "", tk.END, iid=str(contact["id"]),
                values=(contact["name"], contact["phone"], contact["email"],
                        contact["group"], "★ Yes" if contact["favorite"] else "No")
            )
        self.page_label.config(text=f"Page {self.page + 1} / {total_pages}  •  {len(data)} contact(s)")

    def selected_contact(self):
        selected = self.contact_tree.selection() if hasattr(self, "contact_tree") else ()
        if not selected:
            messagebox.showwarning("Select contact", "Please select a contact first.")
            return None
        contact_id = int(selected[0])
        return next((c for c in self.contacts if c["id"] == contact_id), None)

    def add_contact(self):
        self.contact_form()

    def edit_contact(self):
        contact = self.selected_contact()
        if contact:
            self.contact_form(contact)

    def view_contact(self):
        contact = self.selected_contact()
        if contact:
            detail = (
                f"Full name: {contact['name']}\n"
                f"Phone: {contact['phone']}\nEmail: {contact['email']}\n"
                f"Address: {contact['address']}\nGroup: {contact['group']}\n"
                f"Note: {contact['note']}\nFavorite: {'Yes' if contact['favorite'] else 'No'}"
            )
            messagebox.showinfo("Contact Details", detail)

    def delete_contact(self):
        contact = self.selected_contact()
        if not contact:
            return
        if messagebox.askyesno("Confirm deletion",
                               f"Delete contact '{contact['name']}'?"):
            self.contacts.remove(contact)
            self.refresh_contacts()
            messagebox.showinfo("Success", "Contact deleted successfully.")

    def contact_form(self, contact=None):
        editing = contact is not None
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Contact" if editing else "Add Contact")
        dialog.geometry("440x560")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Edit Contact" if editing else "Add New Contact",
                 bg="white", fg=self.navy, font=("Arial", 17, "bold")).pack(
                     anchor="w", padx=25, pady=(22, 15))

        fields = {}
        field_specs = [
            ("Full Name *", "name"), ("Phone Number *", "phone"),
            ("Email", "email"), ("Address", "address"), ("Note", "note")
        ]
        form = tk.Frame(dialog, bg="white")
        form.pack(fill=tk.X, padx=25)
        for label, key in field_specs:
            tk.Label(form, text=label, bg="white", fg="#334155",
                     font=("Arial", 9, "bold")).pack(anchor="w", pady=(7, 3))
            entry = tk.Entry(form, font=("Arial", 10), relief=tk.SOLID, bd=1)
            entry.pack(fill=tk.X, ipady=6)
            if editing:
                entry.insert(0, contact.get(key, ""))
            fields[key] = entry

        tk.Label(form, text="Group", bg="white", fg="#334155",
                 font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 3))
        group_var = tk.StringVar(value=contact.get("group", self.groups[0] if self.groups else "") if editing
                                 else (self.groups[0] if self.groups else ""))
        group_box = ttk.Combobox(form, textvariable=group_var, values=self.groups,
                                 state="readonly", font=("Arial", 10))
        group_box.pack(fill=tk.X, ipady=4)

        favorite_var = tk.BooleanVar(value=contact["favorite"] if editing else False)
        tk.Checkbutton(form, text="Mark as favorite", variable=favorite_var,
                       bg="white", activebackground="white").pack(anchor="w", pady=10)

        def save():
            name = fields["name"].get().strip()
            phone = fields["phone"].get().strip()
            if not name or not phone:
                messagebox.showerror("Validation error", "Full Name and Phone Number are required.", parent=dialog)
                return
            if not phone.isdigit():
                messagebox.showerror("Validation error", "Phone Number must contain digits only.", parent=dialog)
                return
            duplicate = any(c["phone"] == phone and (not editing or c["id"] != contact["id"])
                            for c in self.contacts)
            if duplicate:
                messagebox.showerror("Duplicate phone", "This phone number already exists in your contacts.", parent=dialog)
                return
            if not group_var.get():
                messagebox.showerror("Missing group", "Please create or select a group.", parent=dialog)
                return

            values = {key: entry.get().strip() for key, entry in fields.items()}
            values.update({"group": group_var.get(), "favorite": favorite_var.get()})
            if editing:
                contact.update(values)
            else:
                values["id"] = self.next_contact_id
                self.next_contact_id += 1
                self.contacts.append(values)
            dialog.destroy()
            self.refresh_contacts()
            messagebox.showinfo("Success", "Contact saved successfully.")

        buttons = tk.Frame(dialog, bg="white")
        buttons.pack(fill=tk.X, padx=25, pady=18)
        self.make_button(buttons, "Save", save).pack(side=tk.LEFT, padx=(0, 8))
        self.make_button(buttons, "Cancel", dialog.destroy, "#64748b").pack(side=tk.LEFT)

    def sort_contacts(self, column):
        key_map = {"name": "name", "phone": "phone", "email": "email",
                   "group": "group", "favorite": "favorite"}
        key = key_map[column]
        self.sort_reverse = not self.sort_reverse
        self.contacts.sort(key=lambda c: str(c[key]).lower(), reverse=self.sort_reverse)
        self.page = 0
        self.refresh_contacts()

    def next_page(self):
        self.page += 1
        self.refresh_contacts()

    def previous_page(self):
        self.page = max(0, self.page - 1)
        self.refresh_contacts()

    # -------------------- FAVORITES --------------------
    def show_favorites(self):
        favorites = [c for c in self.contacts if c["favorite"]]
        self.show_contacts(filtered=favorites, title="Favorite Contacts")

    # -------------------- GROUP MANAGEMENT --------------------
    def show_groups(self):
        self.build_shell("Groups")
        self.page_heading("Group Management",
                          "Create, rename and delete groups to organize your contacts")

        body = tk.Frame(self.content, bg="#f8fafc")
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 25))

        left = tk.Frame(body, bg="white", padx=18, pady=18,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 18))
        tk.Label(left, text="Contact Groups", bg="white", fg=self.navy,
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))

        self.group_list = tk.Listbox(left, width=25, height=17,
                                     font=("Arial", 10), relief=tk.FLAT,
                                     highlightthickness=1,
                                     highlightbackground="#cbd5e1",
                                     selectbackground="#bfdbfe",
                                     activestyle="none")
        self.group_list.pack(fill=tk.Y)
        self.group_list.bind("<<ListboxSelect>>", lambda _e: self.refresh_group_details())

        actions = tk.Frame(left, bg="white")
        actions.pack(fill=tk.X, pady=(15, 0))
        self.make_button(actions, "+ Create", self.create_group).pack(fill=tk.X, pady=3)
        self.make_button(actions, "Rename", self.rename_group, "#0f766e").pack(fill=tk.X, pady=3)
        self.make_button(actions, "Delete", self.delete_group, "#dc2626").pack(fill=tk.X, pady=3)

        right = tk.Frame(body, bg="white", padx=20, pady=18,
                         highlightbackground="#e2e8f0", highlightthickness=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="Group Details", bg="white", fg=self.navy,
                 font=("Arial", 14, "bold")).pack(anchor="w")
        self.group_title = tk.Label(right, text="Select a group to view its contacts",
                                    bg="white", fg="#64748b", font=("Arial", 10))
        self.group_title.pack(anchor="w", pady=(8, 15))

        cols = ("name", "phone", "email")
        self.group_tree = ttk.Treeview(right, columns=cols, show="headings", height=13)
        for col, heading, width in [
            ("name", "Full Name", 190), ("phone", "Phone Number", 130),
            ("email", "Email", 200)
        ]:
            self.group_tree.heading(col, text=heading)
            self.group_tree.column(col, width=width, anchor=tk.W)
        self.group_tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_group_list()

    def refresh_group_list(self):
        self.group_list.delete(0, tk.END)
        for group in self.groups:
            count = sum(1 for c in self.contacts if c["group"] == group)
            self.group_list.insert(tk.END, f"{group} ({count})")
        if self.groups:
            self.group_list.selection_set(0)
            self.refresh_group_details()
        else:
            self.group_title.config(text="No groups available.")
            for item in self.group_tree.get_children():
                self.group_tree.delete(item)

    def selected_group(self):
        selection = self.group_list.curselection()
        if not selection:
            messagebox.showwarning("Select group", "Please select a group first.")
            return None
        return self.groups[selection[0]]

    def refresh_group_details(self):
        selection = self.group_list.curselection()
        if not selection:
            return
        group = self.groups[selection[0]]
        self.group_title.config(text=f"Contacts in: {group}")
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        for c in self.contacts:
            if c["group"] == group:
                self.group_tree.insert("", tk.END,
                                       values=(c["name"], c["phone"], c["email"]))

    def create_group(self):
        name = simpledialog.askstring("Create Group", "Enter new group name:", parent=self.root)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showerror("Invalid name", "Group name cannot be empty.")
        elif any(g.lower() == name.lower() for g in self.groups):
            messagebox.showerror("Duplicate group", "This group name already exists.")
        else:
            self.groups.append(name)
            self.refresh_group_list()

    def rename_group(self):
        old_name = self.selected_group()
        if not old_name:
            return
        new_name = simpledialog.askstring("Rename Group", "Enter new group name:",
                                          initialvalue=old_name, parent=self.root)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showerror("Invalid name", "Group name cannot be empty.")
        elif any(g.lower() == new_name.lower() and g != old_name for g in self.groups):
            messagebox.showerror("Duplicate group", "This group name already exists.")
        else:
            index = self.groups.index(old_name)
            self.groups[index] = new_name
            for c in self.contacts:
                if c["group"] == old_name:
                    c["group"] = new_name
            self.refresh_group_list()

    def delete_group(self):
        group = self.selected_group()
        if not group:
            return
        if any(c["group"] == group for c in self.contacts):
            messagebox.showwarning(
                "Cannot delete group",
                "This group still contains contacts. Move those contacts to another group first."
            )
            return
        if messagebox.askyesno("Confirm deletion", f"Delete group '{group}'?"):
            self.groups.remove(group)
            self.refresh_group_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()
