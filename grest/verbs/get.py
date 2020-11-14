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

from inflection import pluralize, singularize
from markupsafe import escape_silent as escape
from neomodel.exception import DoesNotExist

import grest.messages as msg
from grest.exceptions import HTTPException
from grest.utils import serialize
from grest.validation import validate_models


def get(self, primary_id, secondary_model_name=None, secondary_id=None):
    try:
        # patch __log
        self.__log = self._GRest__log

        (primary, secondary) = validate_models(self,
                                               primary_id,
                                               secondary_model_name,
                                               secondary_id)

        primary_selected_item = primary.model.nodes.get_or_none(
            **{primary.selection_field: primary.id})

        if all([primary_selected_item,
                secondary.model,
                secondary.id]):
            # user selected a nested model with 2 keys
            # (from the primary and secondary models)
            # /users/user_id/roles/role_id -> selected role of this user
            # /categories/cat_id/tags/tag_id -> selected tag of this category

            # In this example, the p variable of type Post
            # is the secondary_item
            # (u:User)-[:POSTED]-(p:Post)
            secondary_item = primary_selected_item.get_all(
                secondary.model_name,
                secondary.selection_field,
                secondary.id,
                retrieve_relations=True)

            return serialize({singularize(secondary.model_name):
                              secondary_item})
        elif all([primary_selected_item, secondary.model]):
            # user selected a nested model with primary key
            # (from the primary and the secondary models)
            # /users/user_1/roles -> all roles for this user
            relationships = primary_selected_item.get_all(
                secondary.model_name,
                retrieve_relations=True)
            return serialize({pluralize(secondary.model_name):
                              relationships})
        else:
            # user selected a single item (from the primary model)
            if primary_selected_item:
                return serialize({primary.model_name:
                                  primary_selected_item.to_dict()})
            else:
                raise HTTPException(msg.MODEL_DOES_NOT_EXIST.format(
                    model=primary.model_name), 404)
    except (DoesNotExist, AttributeError) as e:
        self.__log.exception(e.message)
        raise HTTPException(msg.ITEM_DOES_NOT_EXIST, 404)
