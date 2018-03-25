import click
import zipfile
import os
import os.path
from contextlib import closing


template = """\
import sys
sys.path.insert(0, './inner')

import inner.{code_modulename} as inner_module

def dispatch(event, context):
    fun = getattr(inner_module, event['call_descr']['function'])
    args = [event['locals'][arg_name] for arg_name in event['call_descr']['arg_names']]
    return fun(*args)
"""


def zinfo(fname):
    # https://stackoverflow.com/questions/46076543
    zi = zipfile.ZipInfo(fname)
    zi.external_attr = 0o777 << 16
    return zi


@click.command()
@click.argument('code_filename')
@click.argument('zip_filename')
def compile_zipfile(code_filename, zip_filename):
    code_modulename = os.path.splitext(code_filename)[0]
    handler_content = template.format(code_modulename=code_modulename)
    with closing(zipfile.ZipFile(zip_filename, 'x')) as f_zip:
        f_zip.writestr(zinfo('handler.py'), handler_content)
        f_zip.write(code_filename, 'inner/{}'.format(code_filename))
        f_zip.write('pysfn.py')


if __name__ == '__main__':
    compile_zipfile()
