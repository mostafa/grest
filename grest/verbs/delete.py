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
from neomodel import db
from neomodel.exception import DoesNotExist

from grest.exceptions import HTTPException
from grest.utils import serialize


def delete(self, primary_id, secondary_model_name=None, secondary_id=None):
    try:
        primary_id = unquote(primary_id)
        if (secondary_model_name):
            secondary_model_name = unquote(secondary_model_name)
        if (secondary_id):
            secondary_id = unquote(secondary_id)

        primary_model = self.__model__.get("primary")
        primary_selection_field = self.__selection_field__.get("primary")
        secondary_model = secondary_selection_field = None

        # check if there exists a secondary model
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

        if primary_id and secondary_model_name is None and secondary_id is None:
            selected_item = primary_model.nodes.get_or_none(
                **{primary_selection_field: str(escape(primary_id))})

            if selected_item:
                with db.transaction:
                    if selected_item.delete():
                        return serialize(dict(result="OK"))
                    else:
                        raise HTTPException(
                            "There was an error deleting the item.", 500)
            else:
                raise HTTPException("Item does not exist.", 404)
        else:
            if primary_id and secondary_model_name and secondary_id:
                # user either wants to update a relation or
                # has provided invalid information
                primary_selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(escape(primary_id))})

                secondary_selected_item = secondary_model.nodes.get_or_none(
                    **{secondary_selection_field: str(escape(secondary_id))})

                if primary_selected_item and secondary_selected_item:
                    if hasattr(primary_selected_item, secondary_model_name):
                        relation = getattr(
                            primary_selected_item, secondary_model_name)
                        related_item = secondary_selected_item in relation.all()

                        if not related_item:
                            raise HTTPException(
                                "Relation does not exist!", 409)
                        else:
                            with db.transaction:
                                relation.disconnect(
                                    secondary_selected_item)

                            if secondary_selected_item not in relation.all():
                                return serialize(dict(result="OK"))
                            else:
                                raise HTTPException(
                                    "There was an error removing the selected relation.", 500)
                    else:
                        raise HTTPException("Selected " + secondary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid.", 404)
                else:
                    raise HTTPException("Selected " + primary_model.__name__.lower(
                    ) + " does not exist or the provided information is invalid.", 404)
            raise HTTPException(primary_model.__name__ +
                                " id is not provided or is invalid.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
