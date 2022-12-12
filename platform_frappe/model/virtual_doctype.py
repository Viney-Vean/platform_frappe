# Copyright (c) 2022, Mr. Vean Viney and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VirtualDoctype(Document):
    parent_doctype = ""

    def __init__(self, *args, **kwargs):
        self._table_fieldnames = self.get_table_fieldnames()
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    def get_new_parent_doc(self):
        return frappe.new_doc(self.parent_doctype)

    def get_table_fieldnames(self):
        data = set()

        for d in self.get_new_parent_doc().meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_objects(self):
        data = list()

        for d in self.meta.get_table_fields():
            setattr(d, "parent", self.parent_doctype)
            data.append(d)

        return data

    def get_virtual_table_fieldnames(self):
        data = set()

        for d in self.meta.get_table_fields():
            data.update({d.fieldname})

        return data

    def get_table_field_dict(self):
        data = dict()

        for field in self.get_table_field_objects():
            data.update({field.fieldname: {"doctype": field.options, "parent": field.parent, "label": field.label}})

        return data

    def exec_virtual_method(self, fn_name, *args, **kwargs):
        old_doctype = self.doctype
        self.doctype = self.parent_doctype
        getattr(super(), fn_name)(*args, **kwargs)
        self.doctype = old_doctype

    def prepare_data_from_db(self):
        data = frappe.db.get_value(self.parent_doctype, self.name, ["name"], as_dict=1)

        if not data:
            # When reload new form operation, it must ignore another query or another calling function.
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

        self.exec_virtual_method("db_insert", *args, **kwargs)

    def prepare_data_for_db_update(self, *args, **kwargs):
        children_field_dict = self.get_table_field_dict()

        for children_field in self.get_virtual_table_fieldnames():
            children_data = getattr(self, children_field)
            keep_ids = []

            for data_item in children_data:
                setattr(data_item, "parenttype", self.parent_doctype)
                keep_ids.append(data_item.name)

            child_doctype = children_field_dict.get(children_field, {}).get("doctype")
            children = frappe.get_list(child_doctype,
                                       fields=["name"],
                                       filters={"parent": self.name,
                                                "parentfield": children_field,
                                                "parenttype": self.parent_doctype,
                                                "name": ("NOT IN", keep_ids)})

            for del_item in children:
                frappe.delete_doc(child_doctype, del_item.get("name"))

        self.exec_virtual_method("db_update")

    def db_insert(self, *args, **kwargs):
        self.prepare_data_for_db_insert()

    def load_from_db(self):
        self.prepare_data_from_db()

    def db_update(self, *args, **kwargs):
        self.prepare_data_for_db_update()

    def delete(self, ignore_permissions=False):
        self.doctype = self.parent_doctype
        super().delete(ignore_permissions)

    @classmethod
    def get_list(cls, args):
        return frappe.db.get_list(cls.parent_doctype, fields="*")

    @classmethod
    def get_count(cls, args):
        pass

    @classmethod
    def get_stats(cls, args):
        pass
