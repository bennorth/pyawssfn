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


import pysfn as PSF


class TextTooShortError(Exception):
    pass


def get_summary(text):
    if len(text) == 0:
        raise TextTooShortError
    return {'head': text[0]}


def augment_summary(text, summary):
    aug_summary = dict(summary)
    aug_summary['n_characters'] = len(text)
    return aug_summary


def get_n_vowels(text):
    return sum(text.count(v) for v in 'aeiou')


def get_n_spaces(text):
    return text.count(' ')


def format_result(summary, infos):
    """
    Expect inputs of:

    summary --- dict with 'head' and 'n_characters' as keys
    infos --- list of two elements, each a number
    """
    return (f'text starts with {summary["head"]},'
            f' has {summary["n_characters"]} chars,'
            f' {infos[0]} vowels, and'
            f' {infos[1]} spaces')


def format_c_result(summary):
    return f'text starts with "c"; look: "{summary["head"]}"'


# Top-level function, very loosely inspired by the control flow in
#
# https://github.com/aws-samples/lambda-refarch-imagerecognition
#
@PSF.main
def summarise(text):
    try:
        summary = get_summary(text)
    except TextTooShortError:
        raise PSF.Fail('MalformedText', 'text too short')

    if (PSF.StringEquals(summary['head'], 'a')
            or PSF.StringEquals(summary['head'], 'b')):
        summary = PSF.with_retry_spec(augment_summary, (text, summary),
                                      (['States.ALL'], 1, 2, 1.5))

        def get_n_vowels_task():
            result = get_n_vowels(text)
            return result
        #
        def get_n_spaces_task():
            result = get_n_spaces(text)
            return result
        #
        more_info = PSF.parallel(get_n_vowels_task, get_n_spaces_task)

        result = format_result(summary, more_info)
    #
    elif PSF.StringEquals(summary['head'], 'c'):
        result = format_c_result(summary)
    #
    else:
        raise PSF.Fail('MalformedText', 'wrong starting letter')

    return result
