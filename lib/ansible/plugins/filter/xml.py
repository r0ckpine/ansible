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

from xml.parsers.expat import ExpatError, errors

try:
    import xmltodict
    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.six import string_types


def from_xml(data, process_namespaces=False, namespaces=None):
    '''Converts XML string to a dictionary according to the following specification:
        http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
        :param data: XML string
        :returns: a dictionary object
    '''
    if not HAS_XMLTODICT:
        raise AnsibleError('You need to install "xmltodict" prior to running '
                           'from_xml filter')
    if not isinstance(data, string_types):
        raise AnsibleFilterError('from_xml requires a string, '
                                 'got {0} instead'.format(type(data)))
    try:
        return xmltodict.parse(data,
                               dict_constructor=dict,
                               process_namespaces=process_namespaces,
                               namespaces=namespaces)
    except xmltodict.expat.ExpatError as err:
        msg = 'XML Parse error on line {0}, offset {1}: {2}'.format(err.lineno,
                                                                    err.offset,
                                                                    errors.messages[err.code])
        raise AnsibleFilterError(msg)


class FilterModule(object):
    ''' XML filter '''
    def filters(self):
        return {
            'from_xml': from_xml,
        }
