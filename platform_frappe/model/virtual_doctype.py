# Copyright (c) 2022, Mr. Vean Viney and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries


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
                        frm.refresh()
                    }
                });
    """

    parent_doctype = ""

    def __init__(self, *args, **kwargs):
        self._table_fieldnames = self.get_table_fieldnames()
        self.args = args
        self.kwargs = kwargs
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

    def get_virtual_table_fieldnames(self):
        """
            Don't call to protected member directly.
            Ex: self.get_new_parent_doc().meta._table_fields
        """
        data = set()

        for d in self.meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_dict(self):
        data = {}

        for field in self.get_table_field_objects():
            data.update({field.fieldname: {"doctype": field.options, "parent": field.parent, "label": field.label}})

        return data

    def prepare_data_from_db(self):
        data = frappe.db.get_value(self.parent_doctype, self.name, ["name"], as_dict=1)

        if not data:
            # When reload new form operation, it must ignore query to database.
            setattr(self, "__islocal", True)
            return None

        data = frappe.get_doc(self.parent_doctype, self.name).as_dict()
        table_fieldnames = self.get_table_fieldnames()
        form_table_fieldnames = self.get_virtual_table_fieldnames()
        diff_table_fieldnames = table_fieldnames - form_table_fieldnames

        for field_name in diff_table_fieldnames:
            if hasattr(data, field_name):
                del data[field_name]

        self.update(data)

    def prepare_data_for_db_insert(self, *args, **kwargs):
        for children_field in self.get_virtual_table_fieldnames():
            children_data = getattr(self, children_field)

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)

        pre_doct = self.doctype
        self.doctype = self.parent_doctype
        super().db_insert(*args, **kwargs)
        self.doctype = pre_doct

    def prepare_data_for_update(self, *args, **kwargs):
        children_field_dict = self.get_table_field_dict()

        for children_field in self.get_virtual_table_fieldnames():
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

        pre_doct = self.doctype
        self.doctype = self.parent_doctype
        super().db_update()
        self.doctype = pre_doct

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
