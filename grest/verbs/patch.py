#
# Copyright (C) 2017- Mostafa Moradian <mostafamoradian0@gmail.com>
#
# This file is part of grest.
#
# grest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# grest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with grest.  If not, see <http://www.gnu.org/licenses/>.
#

from urllib.request import unquote

from neomodel import db
from neomodel.exception import DoesNotExist

import grest.messages as msg
from grest.exceptions import HTTPException
from grest.utils import serialize
from grest.validation import validate_input, validate_models


def patch(self, request, primary_id):
    try:
        # patch __log
        self.__log = self._GRest__log

        (primary, _) = validate_models(self, primary_id)

        primary_selected_item = None
        if primary.id is not None:
            primary_selected_item = primary.model.nodes.get_or_none(
                **{primary.selection_field: primary.id})

        if primary_selected_item:
            new_item = primary.model()

            # parse input data (validate or not!)
            json_data = validate_input(new_item.validation_rules,
                                       request)

            updated_item = None
            with db.transaction:
                primary_selected_item.__dict__.update(json_data)
                updated_item = primary_selected_item.save()
                updated_item.refresh()

            if updated_item:
                return serialize(dict(result="OK"))
            else:
                raise HTTPException(msg.UPDATE_FAILED, 500)
        else:
            raise HTTPException(msg.ITEM_DOES_NOT_EXIST, 404)
    except DoesNotExist as e:
        self.__log.exception(e.message)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
