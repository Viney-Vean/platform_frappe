from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in platform_frappe/__init__.py
from platform_frappe import __version__ as version

setup(
	name="platform_frappe",
	version=version,
	description="Platform Frappe is an awesome and flexible toolkit for building ERPNext or any platform through frappe framework.",
	author="Mr. VEAN Viney",
	author_email="https://github.com/Viney-Vean/platform_frappe",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
