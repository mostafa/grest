#
# Copyright (C) 2018 Mostafa Moradian <mostafamoradian0@gmail.com>
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

try:
    # For Python 3.0 and later
    from urllib.request import unquote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import unquote

from markupsafe import escape_silent as escape
from inflection import pluralize
from neomodel.exception import DoesNotExist

from grest.exceptions import HTTPException
from grest.utils import serialize


def get(self, primary_id, secondary_model_name=None, secondary_id=None):
    """
    Returns an specified node or its related node
    :param primary_id: unique id of the primary (source) node (model)
    :type: str
    :param secondary_model_name: name of the secondary (destination) node (model)
    :type: str
    :param secondary_id: unique id of the secondary (destination) node (model)
    :type: str

    The equivalent cypher query would be (as an example):
    MATCH (u:User) WHERE n.user_id = "123456789" RETURN n
    Or:
    MATCH (u:User)-[LIKES]->(p:Post) WHERE n.user_id = "123456789" RETURN p
    """
    try:
        # patch __log
        self.__log = self._GRest__log

        primary_id = unquote(primary_id)
        if (secondary_model_name):
            secondary_model_name = unquote(secondary_model_name)
        if (secondary_id):
            secondary_id = unquote(secondary_id)

        primary_model = self.__model__.get("primary")
        primary_selection_field = self.__selection_field__.get("primary")
        secondary_model = secondary_selection_field = None

        if "secondary" in self.__model__:
            secondary_model = self.__model__.get(
                "secondary").get(secondary_model_name)

        if "secondary" in self.__selection_field__:
            secondary_selection_fields = self.__selection_field__.get(
                "secondary")
            secondary_selection_field = secondary_selection_fields.get(
                secondary_model_name)

        if secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary"):
            raise HTTPException("Selected relation does not exist.", 404)

        if primary_id:
            if secondary_model:
                if secondary_id:
                    # user selected a nested model with 2 keys (from the primary and the secondary models)
                    # /users/user_id/roles/role_id -> selected role of this user
                    # /categories/cat_id/tags/tag_id -> selected tag of this category
                    primary_selected_item = primary_model.nodes.get_or_none(
                        **{primary_selection_field: str(escape(primary_id))})
                    if primary_selected_item:
                        if hasattr(primary_selected_item, secondary_model_name):
                            related_item = getattr(
                                primary_selected_item, secondary_model_name).get(
                                **{secondary_selection_field: str(escape(secondary_id))})

                            relationship = getattr(
                                primary_selected_item, secondary_model_name).relationship(related_item)

                            relation = getattr(
                                primary_model, secondary_model_name)

                            if related_item:
                                relation_data = related_item.to_dict()
                                if (relation.definition["model"] is not None):
                                    relation_data.update(
                                        {"relationship": relationship.to_dict()})
                                return serialize({secondary_model.__name__.lower():
                                                    relation_data})
                            else:
                                raise HTTPException("Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid.", 404)
                        else:
                            raise HTTPException("Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid.", 404)
                    else:
                        raise HTTPException("Selected " + primary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid.", 404)
                else:
                    # user selected a nested model with primary key (from the primary and the secondary models)
                    # /users/user_1/roles -> all roles for this user
                    primary_selected_item = primary_model.nodes.get_or_none(
                        **{primary_selection_field: str(escape(primary_id))})
                    if primary_selected_item:
                        if hasattr(primary_selected_item, secondary_model_name):
                            related_items = getattr(
                                primary_selected_item, secondary_model_name).all()

                            if related_items:
                                relationships = []
                                for item in related_items:
                                    item_info = item.to_dict()
                                    relation = getattr(
                                        primary_model, secondary_model_name)
                                    if (relation.definition["model"] is not None):
                                        item_info["relationship"] = item.to_dict(
                                        )
                                    relationships.append(item_info)

                                return serialize({pluralize(secondary_model.__name__.lower()):
                                                    relationships})
                            else:
                                raise HTTPException("Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid.", 404)
                        else:
                            raise HTTPException("Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid.", 404)
                    else:
                        raise HTTPException("Selected " + primary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid.", 404)
            else:
                # user selected a single item (from the primary model)
                selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(escape(primary_id))})

                if selected_item:
                    return serialize({primary_model.__name__.lower(): selected_item.to_dict()})
                else:
                    raise HTTPException("Selected " + primary_model.__name__.lower(
                    ) + " does not exist or the provided information is invalid.", 404)
        else:
            raise HTTPException(primary_model.__name__ +
                                " id is not provided or is invalid.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
