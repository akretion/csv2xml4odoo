from setuptools import setup, find_packages

setup(
    name='csv2xml4odoo',
    version='0.5',
    url='https://github.com/akretion/csv2xml4odoo',
    license='AGPL',
    author='David BEAL',
    author_email='david.beal@akretion.com',
    description='Convert csv to xml in Odoo ERP context',
    install_requires=['click'],
    packages=find_packages(),
    long_description=open('README.md').read(),
    zip_safe=False,
    entry_points=dict(
        console_scripts=['c2x=csv2xml4odoo.c2x:main'])
)
