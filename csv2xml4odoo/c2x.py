#!/usr/bin/env python
# coding: utf-8

# based on this code
# http://code.activestate.com/recipes/577423-convert-csv-to-xml/


# Changelog
# next   use https://github.com/alan-turing-institute/CleverCSV
# v0.4  replace csv.reader by csv.DictReader
# v0.3  make it a library
# v0.2  add more args and help
# v0.1  add args capability


import csv
import glob
import click

BOOLEAN = ('True', 'False')
ERP_HEADER = """<?xml version="1.0"?>
<odoo noupdate="%s">

<!-- This file has been generated by https://github.com/akretion/csv2xml4odoo
     from '%s' source file:
     Please keep original source file up to date: do not edit this file
-->
"""

ERP_FOOTER = """
</odoo>
"""


HELP = """
Convert Odoo csv files in xml files
Csv is easy to maintain but xml data have
'noupdate' and search features

Limitations:

- relation field One2many is NOT SUPPORTED\n
- ambiguous columns: char type but contains float string,
should have special suffix on column name '|char'\n
- relationnal fields notation in csv should be:
myfield_id/id for m2o or myfield_ids/id for m2m

"""


def convert_relationnal_field2xml(tag, value):
    mytag = tag
    for elm in ['/ids', '/id', ':id']:
        mytag = mytag.replace(elm, '')
    if tag[-6:] == 'ids/id':
        # many2many
        xml_ids = value.split(',')
        members = ["ref('%s')" % x for x in xml_ids]
        line = '%s" eval="[(6, 0, [%s])]"/>' % (mytag, ', '.join(members))
    else:
        # many2one
        line = '%s" ref="%s"/>' % (mytag, value)
    return line


def convert_file(csv_file, noupdate=1):
    xml_file = csv_file.replace('.', '_').replace('_csv', '_data.xml')
    xml_data = open(xml_file, 'w')
    xml_data.write(ERP_HEADER % (noupdate, csv_file) + "\n\n\n")
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        tags = reader.fieldnames
        for i in range(len(tags)):
            tags[i] = tags[i].replace(' ', '_')
        if "id" not in tags:
            print ("EXCEPTION: No 'id' column in %s: impossible to generate "
                   "the xml file\n" % csv_file)
        for line in reader:
            print(line)
            if None in line:
                # i.e. too many commas in line (more columns than in header)
                del line[None]
            for key, val in line.items():
                if val is None:
                    continue
                char = False
                # ambiguous column (char type but contains float string)
                # should be mark by suffix |char
                if tags[i][-5:] == '|char':
                    char = True
                numeric = False
                begin = '    <field name="'
                print("%s" % line)
                try:
                    float(val)
                    numeric = True
                except Exception:
                    pass
                if key == 'id':
                    line = ('<record id="%s" model="%s">\n'
                            % (line["id"], csv_file[:-4]))
                elif '/' in key or ':' in key:
                    # relationnal fields
                    xml_suffix = convert_relationnal_field2xml(key, val)
                    line = '%s%s\n' % (begin, xml_suffix)
                elif char:
                    # numeric char field
                    line = '%s%s">%s</field>\n' % (begin, key[:-5], val)
                elif numeric or val in BOOLEAN:
                    line = '%s%s" eval="%s"/>\n' % (begin, key, val)
                else:
                    # basic fields
                    line = '%s%s">%s</field>\n' % (begin, key, val)
                if val or key == 'id':
                    xml_data.write(line)
            xml_data.write('</record>' + "\n\n")
    xml_data.write(ERP_FOOTER)
    xml_data.close()
    print("'%s' file has been created from '%s'" % (xml_file, csv_file))


@click.command(help=HELP)
@click.option('--update', '-u', required=False,
              help="Set 'noupdate' attribute to 0 instead of 1")
@click.argument('file', required=False)
def main(update, file):
    noupdate = 1
    if update:
        noupdate = 0
    converted = False
    if file:
        if file[-4:] in ('.csv', '.CSV'):
            convert_file(file, noupdate)
            converted = True
        else:
            return click.echo("File '%s' has no csv extension" % file)
    else:
        # all csv files are converted
        for csv_file in glob.glob('*.csv'):
            convert_file(csv_file, noupdate)
            converted = True
    if not converted:
        click.echo("Typewrite `c2x --help` for informations")


if __name__ == '__main__':
    main()
