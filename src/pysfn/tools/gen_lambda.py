# Copyright (C) 2018 Ben North
#
# This file is part of 'plausibility argument of concept for compiling
# Python into Amazon Step Function state machine JSON'.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import click
import zipfile
import os
import os.path
from contextlib import closing


package_dir = os.path.split(os.path.split(__file__)[0])[0]
template = """\
import sys
sys.path.insert(0, './inner')

import inner.{code_modulename} as inner_module

def dispatch(event, context):
    fun = getattr(inner_module, event['call_descr']['function'])
    args = [event['locals'][arg_name]
            for arg_name in event['call_descr']['arg_names']]
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
    code_basename = os.path.basename(code_filename)
    code_modulename = os.path.splitext(code_basename)[0]
    handler_content = template.format(code_modulename=code_modulename)
    with closing(zipfile.ZipFile(zip_filename, 'x')) as f_zip:
        f_zip.writestr(zinfo('handler.py'), handler_content)
        f_zip.write(code_filename, 'inner/{}'.format(code_basename))
        f_zip.write(os.path.join(package_dir, 'definition.py'), 'pysfn.py')


if __name__ == '__main__':
    compile_zipfile()
