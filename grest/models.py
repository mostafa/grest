# -*- coding: utf-8 -*-
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

from typing import Iterable
from neomodel import (ArrayProperty, BooleanProperty, DateProperty,
                      DateTimeProperty, EmailProperty, IntegerProperty,
                      JSONProperty, StringProperty, UniqueIdProperty,
                      relationship_manager)
from webargs import fields


class NodeAndRelationHelper(object):
    __validation_rules__ = {}

    def to_dict(self):
        name = 0
        properties = set([prop[name]
                          for prop in self.defined_properties().items()])
        blocked_properties = ["validation_rules"]

        if hasattr(self, "__filtered_fields__"):
            blocked_properties.extend(self.__filtered_fields__)

        # Add null-valued props to filtered_props unique set
        # Add relations to filtered_props unique set
        # Add non-blocked props to filtered_props unique set
        filtered_props = set(
            filter(lambda prop:
                   any([getattr(self, prop) is None,
                        isinstance(getattr(self, prop),
                                   relationship_manager.RelationshipManager),
                        prop in blocked_properties]), properties))

        properties = properties - filtered_props

        result = {key: getattr(self, key) for key in properties}

        return result

    # TODO: Use or remove retrieve_relations kwarg
    def get_all(self,
                secondary_model_name,
                secondary_selection_field=None,
                secondary_id=None,
                retrieve_relations=False):
        """
        Get all relations and their associated relationship information
        """
        # Definition of a relationship between two nodes (class)
        # neomodel.relationship_manager.RelationshipDefinition
        relation_model = getattr(self.__class__, secondary_model_name)
        # Actual relationship object between two nodes which is
        # a submodule of neomodel.relationship_manager like:
        # neomodel.relationship_manager.ZeroOrMore
        relation_obj = getattr(self, secondary_model_name)

        secondary_items = None
        if all([secondary_selection_field, secondary_id]):
            secondary_items = relation_obj.get(
                **{secondary_selection_field: secondary_id})
        else:
            secondary_items = relation_obj.all()

        def get_item(item):
            item_info = item.to_dict()
            # Relationship object between two nodes (actual instance)
            relationship = relation_obj.relationship(item)
            relationship_info = relationship.to_dict()
            if all([relation_model.definition["model"],
                    relationship_info != {}]):
                item_info.update({
                    "relationship": relationship_info
                })
            return item_info

        if secondary_items:
            relationships = []
            if isinstance(secondary_items, Iterable):
                for item in secondary_items:
                    item_info = get_item(item)
                    relationships.append(item_info)
            else:
                item_info = get_item(secondary_items)
                relationships = item_info

            return relationships

        return None

    def relation_exists(self,
                        secondary_model_name,
                        secondary_selected_item):
        if hasattr(self, secondary_model_name):
            relation = getattr(self, secondary_model_name)
            return secondary_selected_item in relation.all()
        return False

    @property
    def validation_rules(self):
        """
        if the user has defined validation rules,
        return that, otherwise construct a set of
        predefined rules and return it.

        All internal GRest methods should use this property.
        """

        if hasattr(self, "__validation_rules__"):
            if len(self.__validation_rules__) > 0:
                # there is a set of user-defined validation rules
                return self.__validation_rules__

        model_types = [
            StringProperty, DateTimeProperty, DateProperty,
            EmailProperty, BooleanProperty, UniqueIdProperty,
            ArrayProperty, IntegerProperty, JSONProperty
        ]

        model_mapping = {
            IntegerProperty: fields.Int,
            StringProperty: fields.Str,
            BooleanProperty: fields.Bool,
            DateTimeProperty: fields.DateTime,
            DateProperty: fields.Date,
            EmailProperty: fields.Email,
            ArrayProperty: fields.List,
            JSONProperty: fields.Dict,
            UniqueIdProperty: fields.UUID
        }

        name = 0
        value = 1

        for field in self.defined_properties().items():
            if field[name] not in self.__validation_rules__:
                if type(field[value]) in model_types:
                    if isinstance(field[value], ArrayProperty):
                        if field[value].unique_index:
                            # what it contains: Array of *String*
                            container = model_mapping[
                                type(field[value].unique_index)]
                        else:
                            # defaults to Raw for untyped ArrayProperty
                            container = fields.Raw

                        self.__validation_rules__[field[name]] = model_mapping[
                            type(field[value])](container,
                                                required=field[value].required)
                    else:
                        self.__validation_rules__[field[name]] = model_mapping[
                            type(field[value])](required=field[value].required)

        return self.__validation_rules__


class Node(NodeAndRelationHelper):
    pass


class Relation(NodeAndRelationHelper):
    pass
