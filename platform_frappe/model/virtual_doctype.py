# Copyright (c) 2022, Mr. Vean Viney and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VirtualDoctype(Document):
    """
        Usage:
            - You must set value to variable parent_doctype.
        Example:
            1. Python File:
                from platform_frappe.model.virtual_doctype import VirtualDoctype

                class CustomerRelative(VirtualDoctype):
                    parent_doctype = "CBP Customer"

            2. Javascript File:
                frappe.ui.form.on('Customer Relative', {
                    after_save: function (frm) {
                        frm.reload_doc();
                    }
                });
    """

    parent_doctype = ""

    def __init__(self, *args, **kwargs):
        self._table_fieldnames = self.get_table_fieldnames()
        super().__init__(*args, **kwargs)

    def get_new_parent_doc(self):
        return frappe.new_doc(self.parent_doctype)

    def get_table_fieldnames(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc()._table_fieldnames
        """
        data = set()

        for d in self.get_new_parent_doc().meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_objects(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc().meta._table_fields
        """
        data = []

        for d in self.meta.get_table_fields():
            setattr(d, "parent", self.parent_doctype)
            data.append(d)

        return data

    def get_table_field_dict(self):
        data = {}

        for field in self.get_table_field_objects():
            data.update({field.fieldname: {"doctype": field.options, "parent": field.parent, "label": field.label}})

        return data

    def prepare_data_from_db(self):
        data = frappe.get_doc(self.parent_doctype, self.name).as_dict()
        self.update(data)

    def prepare_data_for_db_insert(self, *args, **kwargs):
        data = self.get_valid_dict(convert_dates_to_str=True)
        parent_doctype = self.get_new_parent_doc()

        for field, value in data.items():
            if hasattr(parent_doctype, field):
                setattr(parent_doctype, field, value)

        for children_field in self.get_table_fieldnames():
            children_data = getattr(self, children_field)

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)

        parent_doctype.insert(set_name=parent_doctype.name, ignore_mandatory=True)

    def prepare_data_for_update(self, *args, **kwargs):
        data = self.get_valid_dict(convert_dates_to_str=True)
        parent_doctype = self.get_new_parent_doc()
        children_field_dict = self.get_table_field_dict()

        for field, value in data.items():
            if hasattr(parent_doctype, field):
                setattr(parent_doctype, field, value)

        for children_field in self.get_table_fieldnames():
            children_data = getattr(self, children_field)
            keep_ids = []

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)
                keep_ids.append(data_item.name)

            del_child_doctype = children_field_dict.get(children_field, {}).get("doctype")
            del_children = frappe.get_list(del_child_doctype,
                                           fields=["name"],
                                           filters={"parent": self.name,
                                                    "parentfield": children_field,
                                                    "parenttype": self.parent_doctype,
                                                    "name": ("NOT IN", keep_ids)})

            for del_item in del_children:
                frappe.delete_doc(del_child_doctype, del_item.get("name"))

        frappe.db.set_value(self.parent_doctype, self.name, data)
        frappe.db.commit()

    def db_insert(self, *args, **kwargs):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_for_db_insert()

    def load_from_db(self):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_from_db()

    def db_update(self, *args, **kwargs):
        """
            Don't use self.reload() here, the children will not save.
        """
        self.prepare_data_for_update()

    def delete(self, ignore_permissions=False):
        self.doctype = self.parent_doctype
        super().delete(ignore_permissions)

    @classmethod
    def get_list(cls, args):
        data = frappe.db.get_list(cls.parent_doctype, fields="*")
        return data

    @staticmethod
    def get_count(args):
        pass

    @staticmethod
    def get_stats(args):
        pass
