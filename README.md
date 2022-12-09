## Platform Frappe

Platform Frappe is an awesome and flexible toolkit for building ERPNext or any platform through frappe framework.

#### Installation

You can install `platform_frappe` with `bench` from
this [github repository](https://github.com/Viney-Vean/platform_frappe.git): </br>
`$ bench get-app https://github.com/Viney-Vean/platform_frappe.git`

#### Supported platforms

Currently we test `platform_frappe` on Python 3.10 and frappe v14 on these operating systems.

- macOS
- Ubuntu

#### Installation App to Site

`$ bench --site your-site install-app platform_frappe`

#### Usage

- Go to your virtual doctype then start import class `VirtualDoctype`. </br>
- Your class must inherit from class `VirtualDoctype` 
- You must assign variable `parent_doctype` with your original doctype.   </br>
  > from platform_frappe.model.virtual_doctype import VirtualDoctype </br>
  >
  > class ProductVirtual(VirtualDoctype):  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > parent_doctype = "Product"

- Go to your javascript file and add the below script
  > frappe.ui.form.on('Product virtual', {  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > after_save: function (frm) {  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > frm.reload_doc();  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > frm.refresh();  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > }  </br>
  > });

#### Note:
_You can override methods in your virtual doctype._  </br>
###### Example:
  > from platform_frappe.model.virtual_doctype import VirtualDoctype </br>
  >
  > class ProductVirtual(VirtualDoctype):  </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > parent_doctype = "Product" </br></br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > @classmethod </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > def get_list(cls, args): </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > data = frappe.db.get_list(cls.parent_doctype, fields="*", filter={"brand": "Apple"}) </br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
  > return data </br>

#### License

MIT