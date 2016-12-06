# -*- coding: utf-8 -*-
#
# sigi.apps.utils.moodle_ws_api
#
# Copyright (C) 2015  Interlegis
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import json
import urllib2

from django.conf import settings


def get_courses(ids=[], sort_order='', *args, **kwargs):
    ''' Implements core_courses_get_courses function
        @param ids: list of course ids to retrieve, blank for all courses
        @param sort_order: String field to sort the course list. 
                           Prefix wuth - char to indicate reverse order
        @param [field_name[__function]: Filters to apply, in django-style filters. Examples:
                        - idnumber__startswith='evento'
                        - format='topics'
                        - visible.__ge=1
        @return: list of courses that matches with criteria
    '''
    
    extra_filters = []
    
    for k, v in kwargs.items():
        k = k.split('__')
        field = k[0]
        if len(k) == 1:
            k[1] == 'eq'
        filter = {'field': k[0]}
        if k[1] == 'eq':
            filter['function'] = '__eq__'
        elif k[1] == 'ge':
            filter['function'] = '__ge__'
        elif k[1] == 'gt':
            filter['function'] = '__gt__'
        elif k[1] == 'le':
            filter['function'] = '__le__'
        elif k[1] == 'lt':
            filter['function'] = '__lt__'
        elif k[1] == 'ne':
            filter['function'] = '__ne__'
        else:
            filter['function'] = k[1]
        filter['value'] = v
        extra_filters.append(filter)
    
    params = []
    for i, id in enumerate(ids):
        params.append('options[ids][%s]=%s' % (i, id))
    params = '&'.join(params)
    
    url = '%s/%s?wstoken=%s&wsfunction=core_course_get_courses&moodlewsrestformat=json' % (
            settings.SABERES_URL, settings.SABERES_REST_PATH, settings.SABERES_TOKEN)
    
    courses = json.loads(urllib2.urlopen(url, params).read())
    
    if 'errorcode' in courses:
        raise Exception(u"%(errorcode)s (%(exception)s): %(message)s" % courses)
    
    for filter in extra_filters:
        courses = [c for c in courses 
                   if getattr(c[filter['field']], filter['function'])(filter['value'])]
    
    if sort_order:
        if sort_order[0] == '-': # Reverse order
            sort_order = sort_order[1:]
            courses.sort(key=lambda x: x[sort_order])
            courses.reverse()
        else:
            courses.sort(key=lambda x: x[sort_order])
            
    return courses
