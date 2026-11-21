# File: views/contact_group.py
# Phụ trách: Bùi Lê Giang (Cặp A) - Giao diện Contacts, Favorites & Manage Groups

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class ContactGroupView:
    def __init__(self, app):
        self.app = app
        self.search_keyword = ""
        self.group_filter = "All"
        self.sort_by = "name"
        self.sort_asc = True
        self.current_page = 1
        self.page_size = 5
        self.fav_search_keyword = ""

    # =========================================================
    # 7.3. MÀN HÌNH CONTACTS MANAGEMENT (UC-02, 03, 04, 05, 06, 08)
    # =========================================================
    def render_contacts_screen(self):
        header_frame = tk.Frame(self.app.content_area, bg="#ffffff")
        header_frame.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            header_frame,
            text="Contacts Management",
            font=("Arial", 22, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        ).pack(side=tk.LEFT)

        tk.Button(
            header_frame,
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
            command=self.open_add_contact_modal,
        ).pack(side=tk.RIGHT)

        # Thanh Công cụ: Tìm kiếm (UC-03), Lọc Nhóm (UC-07), Sắp xếp (UC-08)
        filter_bar = tk.Frame(
            self.app.content_area,
            bg="#f8fafc",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        filter_bar.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            filter_bar, text="Keyword:", font=("Arial", 9, "bold"), bg="#f8fafc", fg="#334155"
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.search_entry = tk.Entry(
            filter_bar,
            font=("Arial", 10),
            bg="#ffffff",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1,
            width=20,
        )
        self.search_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 6))
        self.search_entry.insert(0, self.search_keyword)
        self.search_entry.bind("<Return>", lambda e: self._apply_search())

        # Lọc theo Nhóm
        tk.Label(
            filter_bar, text="Group:", font=("Arial", 9, "bold"), bg="#f8fafc", fg="#334155"
        ).pack(side=tk.LEFT, padx=(6, 4))

        user_groups = [
            g["name"] for g in self.app.group_service.get_groups_for_ui(self.app.current_user_id)
        ]
        group_options = ["All", "Unassigned"] + user_groups
        self.group_filter_var = tk.StringVar(
            value=self.group_filter if self.group_filter in group_options else "All"
        )
        group_cb = ttk.Combobox(
            filter_bar,
            textvariable=self.group_filter_var,
            values=group_options,
            state="readonly",
            width=12,
            font=("Arial", 9),
        )
        group_cb.pack(side=tk.LEFT, ipady=2, padx=(0, 8))
        group_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_search())

        tk.Button(
            filter_bar,
            text="🔍 Search",
            font=("Arial", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._apply_search,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            filter_bar,
            text="↺ Reset",
            font=("Arial", 9, "bold"),
            bg="#e2e8f0",
            fg="#334155",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._clear_search,
        ).pack(side=tk.LEFT)

        # Điều khiển Sắp xếp (UC-08: Sort by Name or Phone, ASC/DESC)
        tk.Button(
            filter_bar,
            text="↑ ASC" if self.sort_asc else "↓ DESC",
            font=("Arial", 9, "bold"),
            bg="#eff6ff",
            fg="#2563eb",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._toggle_sort_order,
        ).pack(side=tk.RIGHT)

        self.sort_by_var = tk.StringVar(value="Name" if self.sort_by == "name" else "Phone")
        sort_cb = ttk.Combobox(
            filter_bar,
            textvariable=self.sort_by_var,
            values=["Name", "Phone"],
            state="readonly",
            width=8,
            font=("Arial", 9),
        )
        sort_cb.pack(side=tk.RIGHT, ipady=2, padx=(4, 6))
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self._change_sort_field())

        tk.Label(
            filter_bar, text="Sort by:", font=("Arial", 9, "bold"), bg="#f8fafc", fg="#334155"
        ).pack(side=tk.RIGHT)

        # Khung bảng dữ liệu Contacts
        table_container = tk.Frame(
            self.app.content_area,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
        )
        table_container.pack(fill=tk.X)

        th_frame = tk.Frame(table_container, bg="#f8fafc", pady=12, padx=18)
        th_frame.pack(fill=tk.X)
        col_weights = (3, 2, 3, 2, 3)
        for col, w in enumerate(col_weights):
            th_frame.columnconfigure(col, weight=w, uniform="contact_col")

        headers = ["Full Name", "Phone Number", "Email / Note", "Group", "Actions"]
        for idx, text in enumerate(headers):
            tk.Label(
                th_frame,
                text=text,
                font=("Arial", 10, "bold"),
                bg="#f8fafc",
                fg="#64748b",
                anchor="w",
            ).grid(row=0, column=idx, sticky="ew")

        # Truy vấn, tìm kiếm, sắp xếp và phân trang
        contacts = self.app.contact_service.search_contacts(
            self.search_keyword, self.app.current_user_id, self.group_filter
        )
        contacts = self.app.contact_service.sort_contacts(
            contacts, by=self.sort_by, ascending=self.sort_asc
        )
        page_items, self.current_page, total_pages = (
            self.app.contact_service.paginate_contacts(
                contacts, page=self.current_page, page_size=self.page_size
            )
        )

        if not page_items:
            tk.Frame(table_container, bg="#f1f5f9", height=1).pack(fill=tk.X)
            # UC-02 & UC-03 Exception Flow: Thông báo chuẩn theo tài liệu Word
            empty_msg = (
                "No contacts found."
                if (self.search_keyword or self.group_filter != "All")
                else "No contacts available."
            )
            tk.Label(
                table_container,
                text=empty_msg,
                font=("Arial", 11, "bold"),
                bg="#ffffff",
                fg="#64748b",
                pady=30,
            ).pack(fill=tk.X)
        else:
            for contact in page_items:
                tk.Frame(table_container, bg="#f1f5f9", height=1).pack(fill=tk.X)

                row_frame = tk.Frame(table_container, bg="#ffffff", pady=11, padx=18)
                row_frame.pack(fill=tk.X)
                for col, w in enumerate(col_weights):
                    row_frame.columnconfigure(col, weight=w, uniform="contact_col")

                tk.Label(
                    row_frame,
                    text=contact["name"],
                    font=("Arial", 10, "bold"),
                    bg="#ffffff",
                    fg="#0f172a",
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew")

                tk.Label(
                    row_frame,
                    text=contact["phone"],
                    font=("Arial", 10),
                    bg="#ffffff",
                    fg="#334155",
                    anchor="w",
                ).grid(row=0, column=1, sticky="ew")

                sub_info = contact["email"] or contact["note"] or "—"
                tk.Label(
                    row_frame,
                    text=sub_info,
                    font=("Arial", 9),
                    bg="#ffffff",
                    fg="#64748b",
                    anchor="w",
                ).grid(row=0, column=2, sticky="ew")

                tk.Label(
                    row_frame,
                    text=contact["group"],
                    font=("Arial", 9, "bold"),
                    bg="#ffffff",
                    fg="#2563eb",
                    anchor="w",
                ).grid(row=0, column=3, sticky="ew")

                action_cell = tk.Frame(row_frame, bg="#ffffff")
                action_cell.grid(row=0, column=4, sticky="w")

                # UC-02 Extension: View Contact Details (👁)
                tk.Button(
                    action_cell,
                    text="👁",
                    font=("Arial", 10),
                    bg="#f1f5f9",
                    fg="#0f172a",
                    bd=0,
                    width=3,
                    pady=3,
                    cursor="hand2",
                    command=lambda c=contact: self.open_view_details_modal(c),
                ).pack(side=tk.LEFT, padx=(0, 5))

                # UC-07: Mark/Unmark Favorite (★/☆)
                is_fav = contact.get("favorite", False)
                tk.Button(
                    action_cell,
                    text="★" if is_fav else "☆",
                    font=("Arial", 10),
                    bg="#fefce8" if is_fav else "#f8fafc",
                    fg="#eab308" if is_fav else "#94a3b8",
                    bd=0,
                    width=3,
                    pady=3,
                    cursor="hand2",
                    command=lambda c=contact: self._toggle_fav(c),
                ).pack(side=tk.LEFT, padx=(0, 5))

                # UC-05: Update Contact (✎)
                tk.Button(
                    action_cell,
                    text="✎",
                    font=("Arial", 10),
                    bg="#eff6ff",
                    fg="#2563eb",
                    bd=0,
                    width=3,
                    pady=3,
                    cursor="hand2",
                    command=lambda c=contact: self.open_edit_contact_modal(c),
                ).pack(side=tk.LEFT, padx=(0, 5))

                # UC-06: Delete Contact (🗑)
                tk.Button(
                    action_cell,
                    text="🗑",
                    font=("Arial", 10),
                    bg="#fef2f2",
                    fg="#ef4444",
                    bd=0,
                    width=3,
                    pady=3,
                    cursor="hand2",
                    command=lambda c=contact: self.delete_contact(c),
                ).pack(side=tk.LEFT)

        # Thanh Phân trang (UC-08: View paginated contact list)
        pager = tk.Frame(self.app.content_area, bg="#ffffff")
        pager.pack(fill=tk.X, pady=(12, 0))

        tk.Label(
            pager,
            text=f"Showing {len(page_items)} of {len(contacts)} contacts   |   Page {self.current_page} / {total_pages}",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#475569",
        ).pack(side=tk.LEFT)

        tk.Button(
            pager,
            text="Next ▶",
            font=("Arial", 9, "bold"),
            bg="#f1f5f9",
            fg="#0f172a",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: self._change_page(1, total_pages),
        ).pack(side=tk.RIGHT)

        tk.Button(
            pager,
            text="◀ Prev",
            font=("Arial", 9, "bold"),
            bg="#f1f5f9",
            fg="#0f172a",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: self._change_page(-1, total_pages),
        ).pack(side=tk.RIGHT, padx=(0, 6))

    def _apply_search(self):
        self.search_keyword = self.search_entry.get().strip()
        self.group_filter = self.group_filter_var.get()
        self.current_page = 1
        self.app.switch_screen("Contacts")

    def _clear_search(self):
        self.search_keyword = ""
        self.group_filter = "All"
        self.current_page = 1
        self.app.switch_screen("Contacts")

    def _change_sort_field(self):
        self.sort_by = "phone" if self.sort_by_var.get() == "Phone" else "name"
        self.app.switch_screen("Contacts")

    def _toggle_sort_order(self):
        self.sort_asc = not self.sort_asc
        self.app.switch_screen("Contacts")

    def _change_page(self, delta, total_pages):
        new_page = self.current_page + delta
        if 1 <= new_page <= total_pages:
            self.current_page = new_page
            self.app.switch_screen("Contacts")

    def _toggle_fav(self, contact):
        self.app.contact_service.toggle_favorite(contact)
        self.app.switch_screen(self.app.current_screen)

    # =========================================================
    # UC-02 EXTENSION: VIEW CONTACT DETAILS MODAL
    # =========================================================
    def open_view_details_modal(self, contact):
        modal = tk.Toplevel(self.app.root)
        modal.title("Contact Details")
        modal.geometry("420x420")
        modal.configure(bg="#ffffff")
        modal.transient(self.app.root)
        modal.grab_set()

        tk.Label(
            modal,
            text="📇 Contact Full Details",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        ).pack(anchor="w", padx=28, pady=(20, 14))

        info_box = tk.Frame(
            modal,
            bg="#f8fafc",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        info_box.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))

        details = [
            ("Contact ID:", contact["id"]),
            ("Full Name:", contact["name"]),
            ("Phone Number:", contact["phone"]),
            ("Email Address:", contact.get("email") or "Not provided"),
            ("Address:", contact.get("address") or "Not provided"),
            ("Group:", contact.get("group") or "Unassigned"),
            ("Favorite:", "★ Yes" if contact.get("favorite") else "No"),
            ("Notes:", contact.get("note") or "None"),
        ]

        for idx, (label, val) in enumerate(details):
            row = tk.Frame(info_box, bg="#f8fafc")
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row,
                text=label,
                font=("Arial", 10, "bold"),
                bg="#f8fafc",
                fg="#475569",
                width=14,
                anchor="w",
            ).pack(side=tk.LEFT)
            tk.Label(
                row,
                text=val,
                font=("Arial", 10),
                bg="#f8fafc",
                fg="#0f172a",
                anchor="w",
                wraplength=210,
                justify="left",
            ).pack(side=tk.LEFT, fill=tk.X)

        btn_bar = tk.Frame(modal, bg="#ffffff")
        btn_bar.pack(fill=tk.X, padx=28, pady=(0, 18))

        tk.Button(
            btn_bar,
            text="✎ Edit Contact",
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: [modal.destroy(), self.open_edit_contact_modal(contact)],
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_bar,
            text="Close",
            font=("Arial", 10, "bold"),
            bg="#f1f5f9",
            fg="#334155",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=modal.destroy,
        ).pack(side=tk.RIGHT, padx=(0, 8))

    # =========================================================
    # 7.4. MÀN HÌNH FAVORITE CONTACTS (UC-07)
    # =========================================================
    def render_favorites_screen(self):
        header_frame = tk.Frame(self.app.content_area, bg="#ffffff")
        header_frame.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            header_frame, text="⭐", font=("Arial", 20), bg="#ffffff", fg="#f59e0b"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            header_frame,
            text="Favorite Contacts",
            font=("Arial", 22, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        ).pack(side=tk.LEFT)

        # Tìm kiếm nhanh trong mục Yêu thích
        fav_search_box = tk.Frame(header_frame, bg="#ffffff")
        fav_search_box.pack(side=tk.RIGHT)

        self.fav_search_entry = tk.Entry(
            fav_search_box, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1, width=20
        )
        self.fav_search_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 6))
        self.fav_search_entry.insert(0, self.fav_search_keyword)
        self.fav_search_entry.bind("<Return>", lambda e: self._search_favorites())

        tk.Button(
            fav_search_box,
            text="🔍 Search",
            font=("Arial", 9, "bold"),
            bg="#eff6ff",
            fg="#2563eb",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._search_favorites,
        ).pack(side=tk.LEFT)

        table_container = tk.Frame(
            self.app.content_area,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
        )
        table_container.pack(fill=tk.X)

        th_frame = tk.Frame(table_container, bg="#f8fafc", pady=14, padx=24)
        th_frame.pack(fill=tk.X)
        for col, w in enumerate((3, 2, 2, 3)):
            th_frame.columnconfigure(col, weight=w, uniform="favcol")

        for idx, text in enumerate(["Full Name", "Phone Number", "Group", "Actions"]):
            tk.Label(
                th_frame, text=text, font=("Arial", 10, "bold"), bg="#f8fafc", fg="#64748b", anchor="w"
            ).grid(row=0, column=idx, sticky="ew")

        fav_contacts = self.app.contact_service.get_favorites_for_ui(
            self.app.current_user_id, self.fav_search_keyword
        )
        if not fav_contacts:
            tk.Frame(table_container, bg="#f1f5f9", height=1).pack(fill=tk.X)
            tk.Label(
                table_container,
                text="No favorite contacts found.",
                font=("Arial", 11),
                bg="#ffffff",
                fg="#64748b",
                pady=28,
            ).pack(fill=tk.X)
        else:
            for contact in fav_contacts:
                tk.Frame(table_container, bg="#f1f5f9", height=1).pack(fill=tk.X)

                row_frame = tk.Frame(table_container, bg="#ffffff", pady=13, padx=24)
                row_frame.pack(fill=tk.X)
                for col, w in enumerate((3, 2, 2, 3)):
                    row_frame.columnconfigure(col, weight=w, uniform="favcol")

                tk.Label(
                    row_frame,
                    text=contact["name"],
                    font=("Arial", 11, "bold"),
                    bg="#ffffff",
                    fg="#0f172a",
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew")

                tk.Label(
                    row_frame,
                    text=contact["phone"],
                    font=("Arial", 11),
                    bg="#ffffff",
                    fg="#64748b",
                    anchor="w",
                ).grid(row=0, column=1, sticky="ew")

                tk.Label(
                    row_frame,
                    text=contact["group"],
                    font=("Arial", 10, "bold"),
                    bg="#ffffff",
                    fg="#2563eb",
                    anchor="w",
                ).grid(row=0, column=2, sticky="ew")

                act_cell = tk.Frame(row_frame, bg="#ffffff")
                act_cell.grid(row=0, column=3, sticky="w")

                tk.Button(
                    act_cell,
                    text="👁 Details",
                    font=("Arial", 9, "bold"),
                    bg="#f1f5f9",
                    fg="#0f172a",
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda c=contact: self.open_view_details_modal(c),
                ).pack(side=tk.LEFT, padx=(0, 6))

                tk.Button(
                    act_cell,
                    text="★ Unfavorite",
                    font=("Arial", 9, "bold"),
                    bg="#fefce8",
                    fg="#d97706",
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda c=contact: self._toggle_fav(c),
                ).pack(side=tk.LEFT)

    def _search_favorites(self):
        self.fav_search_keyword = self.fav_search_entry.get().strip()
        self.render_favorites_screen()

    # =========================================================
    # 7.5. MÀN HÌNH MANAGE GROUPS (UC-07: Create, Rename, Delete, Classify/Members)
    # =========================================================
    def render_groups_screen(self):
        header_frame = tk.Frame(self.app.content_area, bg="#ffffff")
        header_frame.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header_frame, text="📁", font=("Arial", 20), bg="#ffffff", fg="#2563eb"
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            header_frame,
            text="Manage Groups",
            font=("Arial", 22, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        ).pack(side=tk.LEFT)

        tk.Button(
            header_frame,
            text="+   Add Group",
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            command=self.open_add_group_modal,
        ).pack(side=tk.RIGHT)

        outer_box = tk.Frame(
            self.app.content_area,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            padx=20,
            pady=20,
        )
        outer_box.pack(fill=tk.X)

        groups_data = self.app.group_service.get_groups_for_ui(self.app.current_user_id)
        if not groups_data:
            tk.Label(
                outer_box,
                text="No contact groups created yet. Click '+ Add Group' to create Family, Friends, Colleagues...",
                font=("Arial", 11),
                bg="#ffffff",
                fg="#64748b",
                pady=22,
            ).pack(fill=tk.X)
        else:
            for idx, grp in enumerate(groups_data):
                row_card = tk.Frame(outer_box, bg="#f8fafc", padx=20, pady=14)
                row_card.pack(fill=tk.X, pady=(0 if idx == 0 else 10, 0))

                tk.Label(
                    row_card,
                    text=f"📁   {grp['name']}",
                    font=("Arial", 12, "bold"),
                    bg="#f8fafc",
                    fg="#0f172a",
                ).pack(side=tk.LEFT)

                # Nút Xóa nhóm (Delete group)
                tk.Button(
                    row_card,
                    text="🗑 Delete",
                    font=("Arial", 9, "bold"),
                    bg="#fef2f2",
                    fg="#ef4444",
                    bd=0,
                    padx=10,
                    pady=4,
                    cursor="hand2",
                    command=lambda g=grp: self.delete_group_action(g),
                ).pack(side=tk.RIGHT, padx=(6, 0))

                # Nút Đổi tên nhóm (Rename group)
                tk.Button(
                    row_card,
                    text="✎ Rename",
                    font=("Arial", 9, "bold"),
                    bg="#eff6ff",
                    fg="#2563eb",
                    bd=0,
                    padx=10,
                    pady=4,
                    cursor="hand2",
                    command=lambda g=grp: self.rename_group_action(g),
                ).pack(side=tk.RIGHT, padx=(6, 0))

                # UC-07 Extension: Organize contacts into groups (GroupMember)
                tk.Button(
                    row_card,
                    text="👥 Organize Members",
                    font=("Arial", 9, "bold"),
                    bg="#f0fdf4",
                    fg="#15803d",
                    bd=0,
                    padx=10,
                    pady=4,
                    cursor="hand2",
                    command=lambda g=grp: self.open_group_members_modal(g),
                ).pack(side=tk.RIGHT, padx=(10, 0))

                tk.Label(
                    row_card,
                    text=f"{grp['count']} contacts",
                    font=("Arial", 10, "bold"),
                    bg="#dbeafe",
                    fg="#2563eb",
                    padx=12,
                    pady=4,
                ).pack(side=tk.RIGHT)

    def open_add_group_modal(self):
        group_name = simpledialog.askstring(
            "Create New Group",
            "Enter new group name (e.g., Family, Friends, Colleagues):",
            parent=self.app.root,
        )
        if group_name is not None:
            ok, msg = self.app.group_service.create_group(self.app.current_user_id, group_name)
            if not ok:
                messagebox.showerror("Duplicate / Invalid Group", msg)
            else:
                messagebox.showinfo("Success", msg)
                self.app.switch_screen("Groups")

    def rename_group_action(self, grp):
        new_name = simpledialog.askstring(
            "Rename Group",
            f"Enter new name for group '{grp['name']}':",
            initialvalue=grp["name"],
            parent=self.app.root,
        )
        if new_name is not None and new_name.strip() != grp["name"]:
            ok, msg = self.app.group_service.rename_group(
                self.app.current_user_id, grp["id"], grp["name"], new_name
            )
            if not ok:
                messagebox.showerror("Error", msg)
            else:
                messagebox.showinfo("Success", msg)
                self.app.switch_screen("Groups")

    def delete_group_action(self, grp):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete group '{grp['name']}'?\nContacts in this group will be set to 'Unassigned'.",
        ):
            ok, msg = self.app.group_service.delete_group(
                self.app.current_user_id, grp["id"], grp["name"]
            )
            messagebox.showinfo("Deleted", msg)
            self.app.switch_screen("Groups")

    # =========================================================
    # UC-07 EXTENSION & BẢNG 6.4: QUẢN LÝ THÀNH VIÊN NHÓM (GroupMember)
    # =========================================================
    def open_group_members_modal(self, grp):
        modal = tk.Toplevel(self.app.root)
        modal.title(f"Organize Contacts in '{grp['name']}'")
        modal.geometry("620x480")
        modal.configure(bg="#ffffff")
        modal.transient(self.app.root)
        modal.grab_set()

        tk.Label(
            modal,
            text=f"📁 Group Members: {grp['name']}",
            font=("Arial", 15, "bold"),
            bg="#ffffff",
            fg="#0f172a",
        ).pack(anchor="w", padx=24, pady=(18, 10))

        # Khu vực gán liên hệ vào nhóm kèm Role & Nickname (Bảng GroupMember)
        assign_box = tk.Frame(
            modal,
            bg="#f8fafc",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        assign_box.pack(fill=tk.X, padx=24, pady=(0, 14))

        all_contacts = self.app.contact_service.get_contacts_for_ui(self.app.current_user_id)
        contact_choices = [f"{c['id']} - {c['name']} ({c['phone']})" for c in all_contacts]

        tk.Label(assign_box, text="Contact:", font=("Arial", 9, "bold"), bg="#f8fafc").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        contact_var = tk.StringVar(value=contact_choices[0] if contact_choices else "")
        contact_cb = ttk.Combobox(
            assign_box,
            textvariable=contact_var,
            values=contact_choices,
            state="readonly",
            width=24,
            font=("Arial", 9),
        )
        contact_cb.grid(row=0, column=1, padx=(0, 10), pady=4)

        tk.Label(assign_box, text="Role:", font=("Arial", 9, "bold"), bg="#f8fafc").grid(
            row=0, column=2, sticky="w", padx=(0, 4)
        )
        role_ent = tk.Entry(assign_box, font=("Arial", 9), width=10, relief=tk.SOLID, bd=1)
        role_ent.grid(row=0, column=3, padx=(0, 10))
        role_ent.insert(0, "Member")

        tk.Label(assign_box, text="Nickname:", font=("Arial", 9, "bold"), bg="#f8fafc").grid(
            row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0)
        )
        nick_ent = tk.Entry(assign_box, font=("Arial", 9), width=26, relief=tk.SOLID, bd=1)
        nick_ent.grid(row=1, column=1, sticky="w", pady=(6, 0))

        list_container = tk.Frame(
            modal,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
        )
        list_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        def refresh_members():
            for w in list_container.winfo_children():
                w.destroy()

            th = tk.Frame(list_container, bg="#f8fafc", padx=14, pady=10)
            th.pack(fill=tk.X)
            for c_i, w_i in enumerate((3, 2, 2, 2, 2)):
                th.columnconfigure(c_i, weight=w_i, uniform="gmcol")
            for idx, text in enumerate(["Name", "Phone", "Role", "Nickname", "Action"]):
                tk.Label(
                    th, text=text, font=("Arial", 9, "bold"), bg="#f8fafc", fg="#64748b", anchor="w"
                ).grid(row=0, column=idx, sticky="ew")

            members = self.app.group_service.get_group_members(
                self.app.current_user_id, grp["id"], grp["name"]
            )
            if not members:
                tk.Label(
                    list_container,
                    text="No contacts in this group yet.",
                    font=("Arial", 10),
                    bg="#ffffff",
                    fg="#64748b",
                    pady=20,
                ).pack(fill=tk.X)
            else:
                for m in members:
                    tk.Frame(list_container, bg="#f1f5f9", height=1).pack(fill=tk.X)
                    rf = tk.Frame(list_container, bg="#ffffff", padx=14, pady=8)
                    rf.pack(fill=tk.X)
                    for c_i, w_i in enumerate((3, 2, 2, 2, 2)):
                        rf.columnconfigure(c_i, weight=w_i, uniform="gmcol")

                    tk.Label(
                        rf, text=m["fullName"], font=("Arial", 10, "bold"), bg="#ffffff", anchor="w"
                    ).grid(row=0, column=0, sticky="ew")
                    tk.Label(
                        rf, text=m["phoneNumber"], font=("Arial", 9), bg="#ffffff", fg="#64748b", anchor="w"
                    ).grid(row=0, column=1, sticky="ew")
                    tk.Label(
                        rf, text=m["memberRole"], font=("Arial", 9), bg="#ffffff", fg="#2563eb", anchor="w"
                    ).grid(row=0, column=2, sticky="ew")
                    tk.Label(
                        rf, text=m["nickname"] or "—", font=("Arial", 9), bg="#ffffff", fg="#475569", anchor="w"
                    ).grid(row=0, column=3, sticky="ew")

                    tk.Button(
                        rf,
                        text="✖ Remove",
                        font=("Arial", 8, "bold"),
                        bg="#fef2f2",
                        fg="#ef4444",
                        bd=0,
                        padx=8,
                        pady=3,
                        cursor="hand2",
                        command=lambda cid=m["contactID"]: remove_member(cid),
                    ).grid(row=0, column=4, sticky="w")

        def add_member():
            sel = contact_var.get()
            if not sel:
                messagebox.showwarning("No Contact", "Please add a contact first!", parent=modal)
                return
            cid = sel.split(" - ")[0].strip()
            self.app.group_service.assign_contact_to_group(
                grp["id"], grp["name"], cid, role_ent.get(), nick_ent.get()
            )
            refresh_members()
            self.render_groups_screen()

        def remove_member(cid):
            self.app.group_service.remove_contact_from_group(grp["id"], cid)
            refresh_members()
            self.render_groups_screen()

        tk.Button(
            assign_box,
            text="+ Assign to Group",
            font=("Arial", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=add_member,
        ).grid(row=1, column=2, columnspan=2, sticky="e", pady=(6, 0))

        refresh_members()

    # =========================================================
    # HỘP THOẠI THÊM / SỬA / XÓA LIÊN HỆ (UC-04, UC-05, UC-06)
    # =========================================================
    def open_add_contact_modal(self):
        self._open_contact_modal(title="Add New Contact", contact=None)

    def open_edit_contact_modal(self, contact):
        self._open_contact_modal(title="Update Contact", contact=contact)

    def _open_contact_modal(self, title, contact=None):
        modal = tk.Toplevel(self.app.root)
        modal.title(title)
        modal.geometry("430x560")
        modal.configure(bg="#ffffff")
        modal.transient(self.app.root)
        modal.grab_set()

        tk.Label(
            modal, text=title, font=("Arial", 16, "bold"), bg="#ffffff", fg="#0f172a"
        ).pack(anchor="w", padx=28, pady=(18, 10))

        form = tk.Frame(modal, bg="#ffffff")
        form.pack(fill=tk.BOTH, expand=True, padx=28)

        tk.Label(
            form, text="Full Name *", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155"
        ).pack(anchor="w", pady=(0, 2))
        name_entry = tk.Entry(form, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        name_entry.pack(fill=tk.X, ipady=5, pady=(0, 8))

        tk.Label(
            form,
            text="Phone Number (10 digits, Unique) *",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#334155",
        ).pack(anchor="w", pady=(0, 2))
        phone_entry = tk.Entry(form, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        phone_entry.pack(fill=tk.X, ipady=5, pady=(0, 8))

        tk.Label(
            form, text="Email Address", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155"
        ).pack(anchor="w", pady=(0, 2))
        email_entry = tk.Entry(form, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        email_entry.pack(fill=tk.X, ipady=5, pady=(0, 8))

        tk.Label(
            form, text="Address", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155"
        ).pack(anchor="w", pady=(0, 2))
        address_entry = tk.Entry(form, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        address_entry.pack(fill=tk.X, ipady=5, pady=(0, 8))

        tk.Label(
            form, text="Group (Select or type new)", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155"
        ).pack(anchor="w", pady=(0, 2))
        groups_list = self.app.group_service.get_groups_for_ui(self.app.current_user_id)
        group_names = ["Unassigned"] + [g["name"] for g in groups_list]
        group_var = tk.StringVar(
            value=contact["group"] if contact and contact.get("group") else group_names[0]
        )
        group_cb = ttk.Combobox(
            form, textvariable=group_var, values=group_names, font=("Arial", 10)
        )
        group_cb.pack(fill=tk.X, ipady=4, pady=(0, 8))

        tk.Label(
            form, text="Notes", font=("Arial", 10, "bold"), bg="#ffffff", fg="#334155"
        ).pack(anchor="w", pady=(0, 2))
        note_entry = tk.Entry(form, font=("Arial", 10), bg="#f8fafc", relief=tk.SOLID, bd=1)
        note_entry.pack(fill=tk.X, ipady=5, pady=(0, 8))

        fav_var = tk.BooleanVar(value=contact.get("favorite", False) if contact else False)
        tk.Checkbutton(
            form,
            text="Mark as Favorite Contact (⭐)",
            variable=fav_var,
            bg="#ffffff",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(2, 8))

        if contact:
            name_entry.insert(0, contact["name"])
            phone_entry.insert(0, contact["phone"])
            email_entry.insert(0, contact.get("email", ""))
            address_entry.insert(0, contact.get("address", ""))
            note_entry.insert(0, contact.get("note", ""))

        def save_action():
            chosen_group = group_var.get().strip() or "Unassigned"
            existing_names = [
                g["name"].lower()
                for g in self.app.group_service.get_groups_for_ui(self.app.current_user_id)
            ]
            if chosen_group != "Unassigned" and chosen_group.lower() not in existing_names:
                self.app.group_service.create_group(self.app.current_user_id, chosen_group)

            ok, msg = self.app.contact_service.validate_and_save(
                user_id=self.app.current_user_id,
                name=name_entry.get().strip(),
                phone=phone_entry.get().strip(),
                group_name=chosen_group,
                is_favorite=fav_var.get(),
                email=email_entry.get().strip(),
                address=address_entry.get().strip(),
                note=note_entry.get().strip(),
                contact_id=contact["id"] if contact else None,
            )
            if not ok:
                messagebox.showerror("Validation Error", msg, parent=modal)
                return

            messagebox.showinfo("Success", msg, parent=modal)
            modal.destroy()
            self.app.switch_screen("Contacts")

        btn_frame = tk.Frame(modal, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=28, pady=(0, 18))

        tk.Button(
            btn_frame,
            text="Save Contact",
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=save_action,
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 10, "bold"),
            bg="#f1f5f9",
            fg="#334155",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=modal.destroy,
        ).pack(side=tk.RIGHT, padx=(0, 8))

    def delete_contact(self, contact):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete contact '{contact['name']}' ({contact['phone']})?",
        ):
            self.app.contact_service.delete_contact(contact["id"])
            messagebox.showinfo("Deleted", f"Contact '{contact['name']}' has been deleted.")
            self.app.switch_screen("Contacts")