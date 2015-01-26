# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

import json
import jsonschema
import aiohttp.web
import logging
import sys
from ..version import __version__

log = logging.getLogger(__name__)


class Response(aiohttp.web.Response):

    def __init__(self, route=None, output_schema=None, headers={}, **kwargs):

        self._route = route
        self._output_schema = output_schema
        headers['X-Route'] = self._route
        headers['Server'] = "Python/{0[0]}.{0[1]} GNS3/{1}".format(sys.version_info, __version__)
        super().__init__(headers=headers, **kwargs)

    """
    Set the response content type to application/json and serialize
    the content.

    :param anwser The response as a Python object
    """

    def json(self, answer):
        """Pass a Python object and return a JSON as answer"""

        print(self.headers)
        self.content_type = "application/json"
        if hasattr(answer, '__json__'):
            answer = answer.__json__()
        if self._output_schema is not None:
            try:
                jsonschema.validate(answer, self._output_schema)
            except jsonschema.ValidationError as e:
                log.error("Invalid output schema {} '{}' in schema: {}".format(e.validator,
                                                                               e.validator_value,
                                                                               json.dumps(e.schema)))
                raise aiohttp.web.HTTPBadRequest(text="{}".format(e))
        self.body = json.dumps(answer, indent=4, sort_keys=True).encode('utf-8')
