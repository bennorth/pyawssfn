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


def StringEquals(x, y):
    assert isinstance(x, str)
    assert isinstance(y, str)
    return x == y


class Fail(Exception):
    def __init__(self, label, message):
        self.label = label
        self.message = message

    def __str__(self):
        return f'{self.label}: {self.message}'


def parallel(*funs):
    return [f() for f in funs]


def with_retry_spec(fun, args, *retry_specs):
    return fun(*args)


def main(fun):
    return fun
