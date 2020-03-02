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

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.six import string_types


def from_table(data):
    '''Parse prettytable output to a list of dictionaries.
    :param data: A string representation of the PrettyTable output.
    :returns: A list of dictionaries.

    Example:
    +---------+---------+---------+
    | Field A | Field B |   ...   |
    +---------+---------+---------+
    | val 1a  | val 1b  |   ...   |
    | val 2a  | val 2b  |   ...   |
    |   ...   |   ...   |   ...   |
    +---------+---------+---------+
    to
    [
        {'Field A': 'val 1a', 'Field B': 'val 1b', ...},
        {'Field A': 'val 2a', 'Field B': 'val 2b', ...},
        {...},
    ]
    '''
    if not isinstance(data, string_types):
        raise AnsibleFilterError("from_prettytable requires a string, got %s instead" % type(data))

    result = []
    header = []
    line_num = 0
    for line in data.splitlines():
        if line_num == 0:
            if line.startswith('+') and line.endswith('+'):
                border = [pos for pos, char in enumerate(line) if char == '+']
            else:
                break
        elif line_num == 1:
            if line.startswith('|') and line.endswith('|'):
                header = [line[start + 1:end].strip()
                          for start, end in zip(border[:], border[1:])]
            else:
                break
        else:
            if line.startswith('|') and line.endswith('|'):
                result.append(dict(zip(header,
                                       [line[start + 1:end].strip()
                                        for start, end in zip(border[:], border[1:])])))
            else:
                # simply ignore the grid lines or other unformatted lines
                continue
        line_num += 1
    return result


class FilterModule(object):
    ''' PrettyTable filter '''
    def filters(self):
        return {
            'from_table': from_table
        }
