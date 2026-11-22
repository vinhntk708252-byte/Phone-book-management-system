
# Phụ trách: Nguyễn Quốc Cường 

from dao.contact_dao import ContactDAO
from dao.group_dao import GroupDAO
from models.entities import Validator

class ContactService:
    def __init__(self, contact_dao=None):
        self.contact_dao = contact_dao or ContactDAO()

    def _map(self, r):
        return {
            "id": r["contactID"], "name": r["fullName"], "phone": r["phoneNumber"],
            "email": r.get("email") or "", "address": r.get("address") or "",
            "note": r.get("note") or "", "group": r.get("groupName") or "Unassigned",
            "favorite": bool(r["isFavorite"]),
        }

    def get_contacts_for_ui(self, uid):
        return [self._map(r) for r in self.contact_dao.get_all_contacts(uid)]

    def get_favorites_for_ui(self, uid, kw=""):
        kw = kw.strip().lower()
        items = [self._map(r) for r in self.contact_dao.get_favorite_contacts(uid)]
        return [c for c in items if kw in c["name"].lower() or kw in c["phone"].lower()] if kw else items

    def search_contacts(self, kw, uid, group_filter="All"):
        kw = kw.strip().lower()
        res = []
        for c in self.get_contacts_for_ui(uid):
            if group_filter not in ("", "All") and c["group"] != group_filter:
                continue
            if kw and kw not in c["name"].lower() and kw not in c["phone"].lower():
                continue
            res.append(c)
        return res

    def sort_contacts(self, contacts, by="name", ascending=True):
        key_fn = (lambda x: x["phone"]) if by == "phone" else (lambda x: x["name"].lower())
        return sorted(contacts, key=key_fn, reverse=not ascending)

    def paginate_contacts(self, contacts, page=1, page_size=5):
        total = max(1, (len(contacts) + page_size - 1) // page_size)
        page = max(1, min(page, total))
        start = (page - 1) * page_size
        return contacts[start : start + page_size], page, total

    def validate_and_save(self, uid, name, phone, group="Unassigned", fav=False, email="", address="", note="", contact_id=None):
        ok, err = Validator.validate_contact_input(name, phone, email)
        if not ok:
            return False, err
        if self.contact_dao.phone_exists(phone, uid, exclude_id=contact_id):
            return False, "This phone number already exists in your contacts."
        grp = group.strip() or "Unassigned"
        if contact_id:
            self.contact_dao.update_contact(contact_id, name, phone, grp, fav, email, address, note)
            return True, "Contact updated successfully."
        self.contact_dao.add_contact(uid, name, phone, grp, fav, email, address, note)
        return True, "New contact added successfully."

    def toggle_favorite(self, c):
        self.contact_dao.toggle_favorite(c["id"], not c.get("favorite", False))

    def delete_contact(self, cid):
        self.contact_dao.delete_contact(cid)

class GroupService:
    def __init__(self, group_dao=None):
        self.group_dao = group_dao or GroupDAO()

    def get_groups_for_ui(self, uid):
        return [{"id": g["groupID"], "name": g["groupName"], "count": g["count"]} for g in self.group_dao.get_all_groups(uid)]

    def create_group(self, uid, name):
        name = (name or "").strip()
        if not name:
            return False, "Group name cannot be empty."
        if self.group_dao.group_exists(uid, name):
            return False, f"Group '{name}' already exists."
        self.group_dao.create_group(uid, name)
        return True, f"Group '{name}' created."

    def rename_group(self, uid, gid, old_name, new_name):
        name = (new_name or "").strip()
        if not name:
            return False, "New group name cannot be empty."
        if self.group_dao.group_exists(uid, name, exclude_id=gid):
            return False, f"Group '{name}' already exists."
        self.group_dao.rename_group(gid, uid, old_name, name)
        return True, f"Group renamed to '{name}'."

    def delete_group(self, uid, gid, name):
        self.group_dao.delete_group(gid, uid, name)
        return True, f"Group '{name}' deleted."

    def get_group_members(self, uid, gid, name):
        return self.group_dao.get_group_members(uid, gid, name)

    def assign_contact_to_group(self, gid, name, cid, role="Member", nick=""):
        self.group_dao.assign_contact_to_group(gid, name, cid, role.strip() or "Member", nick.strip())
        return True, "Assigned to group."

    def remove_contact_from_group(self, gid, cid):
        self.group_dao.remove_contact_from_group(gid, cid)
