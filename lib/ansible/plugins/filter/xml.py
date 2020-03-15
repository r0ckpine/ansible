# (c) 2020, Noboru Iwamatsu <n_iwamatsu@fujitsu.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from collections import defaultdict
from functools import partial
import xml.etree.ElementTree as etree

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types, text_type


def etree_to_dict(elm, expand_to_list=()):
    """ Converts ElementTree to dictionary.
        You can use the force_list argument to force get a list as a
        child, even if the element has only one sub-element.
        :param elm: xml.etree.ElementTree object
        :param expand_to_list: a tuple of tag names to force expand to list:
        :returns: dictionary object
    """
    d = {elm.tag: {} if elm.attrib else None}
    children = list(elm)
    if children:
        dd = defaultdict(list)
        for dc in map(partial(etree_to_dict,
                              expand_to_list=expand_to_list),
                      children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {elm.tag: {k: v[0] if len(v) == 1 and k not in expand_to_list
                       else v for k, v in dd.items()}}
    if elm.attrib:
        d[elm.tag].update(('@' + k, v) for k, v in elm.attrib.items())
    if elm.text:
        text = elm.text.strip()
        if children or elm.attrib:
            if text:
                d[elm.tag]['#text'] = text
        else:
            d[elm.tag] = text
    return d


def from_xml(string, expand_to_list=()):
    '''Converts XML string to a dictionary according to the following specification:
    http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
        :param string: XML string
        :param expand_to_list: a tuple of tag names to force expand to list
        :returns: a dictionary object
    '''
    try:
        root = etree.fromstring(string)
    except etree.ParseError as err:
        row, column = err.position
        msg = 'XML parse error on row: {}, column: {}'.format(row, column)
        raise AnsibleFilterError(msg)
    return etree_to_dict(root, expand_to_list=expand_to_list)


class FilterModule(object):
    ''' XML filter '''
    def filters(self):
        return {
            'from_xml': from_xml,
        }
