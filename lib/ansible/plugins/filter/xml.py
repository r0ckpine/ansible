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
import re

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.six import string_types


ns_pattern = r'^{(.+?)}(.+?)$'


def _tag_name(tag, ns_prefixes=None):
    if not ns_prefixes:
        ns_prefixes = {}
    name = re.sub(ns_pattern, r'\1:\2', tag)
    for k, v in ns_prefixes.items():
        if name.startswith(k):
            if v is None:
                return name.replace(k + ':', '')
            return name.replace(k, v)
    return name


def etree_to_dict(elm, ns_prefixes=None, alwayslist=None):
    """ Converts ElementTree to dictionary.
        You can use the force_list argument to force get a list as a
        child, even if the element has only one sub-element.
        :param elm: xml.etree.ElementTree object
        :param ns_prefixes: a dictionary of namespace and the prefix
        :param alwayslist: a list of tag names to force expand to list:
        :returns: dictionary object
    """
    children = list(elm)

    tag = _tag_name(elm.tag, ns_prefixes=ns_prefixes)
    # Empty element, it can have attributes.
    d = {tag: {} if elm.attrib else None}
    text = []

    if children:
        dd = defaultdict(list)
        for dc in map(partial(etree_to_dict, ns_prefixes=ns_prefixes, alwayslist=alwayslist), children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {tag: {k: v[0] if len(v) == 1 and k not in alwayslist else v for k, v in dd.items()}}

        # If the element is Semi-structured elements, which has textual content
        # mixed up with child elements, collect the text and children's tail.
        if elm.text and elm.text.strip():
            text.append(elm.text.strip())
        for e in children:
            if e.tail and e.tail.strip():
                text.append(e.tail.strip())

    if elm.attrib:
        d[tag].update(('@' + k, v) for k, v in elm.attrib.items())

    if len(text) == 1:
        d[tag]['#text'] = text[0]
    elif len(text) >= 2:
        d[tag]['#text'] = text
    elif elm.text and elm.text.strip():
        if elm.attrib:
            d[tag]['#text'] = elm.text.strip()
        else:
            d[tag] = elm.text.strip()

    return d


def from_xml(data, ns_prefixes=None, alwayslist=None):
    '''Converts XML string to a dictionary according to the following specification:
        http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
        :param data: XML string
        :returns: a dictionary object
    '''
    if not HAS_LXML:
        raise AnsibleError('You need to install "lxml" prior to running '
                           'from_xml filter')
    if not isinstance(data, string_types):
        raise AnsibleFilterError('from_xml input requires a string, got {0} instead'.format(type(data)))
    if not ns_prefixes:
        ns_prefixes = {}
    elif not isinstance(ns_prefixes, dict):
        raise AnsibleFilterError('ns_prefixes must be a dict')
    if not alwayslist:
        alwayslist = []
    elif not isinstance(alwayslist, list):
        raise AnsibleFilterError('alwayslist must be a list')
    try:
        root = etree.fromstring(data)
    except etree.ParseError as err:
        row, column = err.position
        msg = 'XML parse error on row: {0}, column: {1}'.format(row, column)
        raise AnsibleFilterError(msg)
    return etree_to_dict(root, ns_prefixes=ns_prefixes, alwayslist=alwayslist)


class FilterModule(object):
    ''' XML filter '''
    def filters(self):
        return {
            'from_xml': from_xml,
        }
