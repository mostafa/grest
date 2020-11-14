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
from neomodel.exception import DoesNotExist, RequiredProperty, UniqueProperty

import grest.messages as msg
from grest.exceptions import HTTPException
from grest.utils import serialize
from grest.validation import validate_input, validate_models


def post(self,
         request,
         primary_id=None,
         secondary_model_name=None,
         secondary_id=None):
    try:
        # patch __log
        self.__log = self._GRest__log

        (primary, secondary) = validate_models(self,
                                               primary_id,
                                               secondary_model_name,
                                               secondary_id)

        primary_selected_item = None
        if primary.id is not None:
            primary_selected_item = primary.model.nodes.get_or_none(
                **{primary.selection_field: primary.id})

        secondary_selected_item = None
        if secondary.id is not None:
            secondary_selected_item = secondary.model.nodes.get_or_none(
                **{secondary.selection_field: secondary.id})

        if all([primary_selected_item,
                secondary_selected_item,
                secondary.model,
                secondary.id]):
            # user either wants to update a relation or
            # has provided invalid information
            if hasattr(primary_selected_item, secondary.model_name):
                relation_exists = primary_selected_item.relation_exists(
                    secondary.model_name,
                    secondary_selected_item)
                if relation_exists:
                    # There is an existing relation
                    raise HTTPException(msg.RELATION_EXISTS, 409)
                else:
                    # Get relation between primary and secondary objects
                    relation = getattr(
                        primary_selected_item,
                        secondary.model_name)

                    # If there is a relation model between the two,
                    # validate requests based on that
                    relation_model = relation.definition["model"]
                    json_data = {}
                    if relation_model is not None:
                        # TODO: find a way to validate relationships
                        json_data = request.get_json(silent=True)

                    with db.transaction:
                        if not json_data:
                            related_item = relation.connect(
                                secondary_selected_item)
                        else:
                            related_item = relation.connect(
                                secondary_selected_item, json_data)

                        if related_item:
                            return serialize(dict(result="OK"))
                        else:
                            raise HTTPException(msg.RELATION_DOES_NOT_EXIST,
                                                404)
        elif all([primary_selected_item is None,
                  secondary.model is None,
                  secondary.id is None]):
            new_item = primary.model()

            # parse input data (validate or not!)
            json_data = validate_input(new_item.validation_rules,
                                       request)

            # user wants to add a new item (from the primary model)
            new_item = primary.model.nodes.get_or_none(**json_data)

            if not new_item:
                with db.transaction:
                    new_item = primary.model(**json_data).save()
                    new_item.refresh()

                return serialize({primary.selection_field:
                                  getattr(new_item,
                                          primary.selection_field)})
            else:
                raise HTTPException(msg.ITEM_EXISTS.format(
                    item=primary.model_name), 409)
        else:
            raise HTTPException(msg.BAD_REQUEST, 400)
    except (DoesNotExist, AttributeError) as e:
        self.__log.exception(e.message)
        raise HTTPException(msg.ITEM_DOES_NOT_EXIST, 404)
    except UniqueProperty as e:
        self.__log.exception(e.message)
        raise HTTPException(msg.NON_UNIQUE_PROPERTIY, 409)
    except RequiredProperty as e:
        self.__log.exception(e.message)
        raise HTTPException(msg.REQUIRE_PROPERTY_MISSING, 500)
