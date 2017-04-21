from flask import jsonify, request, g
from flask_classful import FlaskView, route
from utils import authenticate, authorize
import markupsafe
import inflect
from neomodel import db, StructuredNode
from neomodel.exception import UniqueProperty, DoesNotExist
from global_config import DEBUG, QUERY_LIMIT
from webargs.flaskparser import parser
from webargs.core import WebargsError, ValidationError
from autologging import logged
from webargs import fields


@logged
class grest(FlaskView):
    __model__ = {"primary": StructuredNode, "secondary": {}}
    __selection_field__ = {"primary": "id", "secondary": {}}

    def __init__(self):
        super(self.__class__, self)

    @authenticate
    @authorize
    def index(self):
        try:
            primary_model = self.__model__.get("primary")
            query_data = None
            validation_rules = {
                "skip": fields.Int(required=False, validate=lambda s: s >= 0),
                "limit": fields.Int(required=False, validate=lambda l: l >= 1 and l <= 100)
            }

            # parse input data (validate or not!)
            try:
                query_data = parser.parse(validation_rules, request)
            except Exception as e:
                self.__log.debug("Validation failed!")
                return jsonify(errors=["One or more of the required fields is missing or incorrect."]), 422

            start = query_data.get("skip")
            if (start):
                start = int(start)
            else:
                start = 0

            count = query_data.get("limit")
            if (count):
                count = start + int(count)
            else:
                count = start + QUERY_LIMIT

            total_items = len(primary_model.nodes)

            if (total_items <= 0):
                return jsonify(errors=["No " + primary_model.__name__.lower() + " exists."]), 404

            if (start > total_items):
                return jsonify(errors=["One or more of the required fields is incorrect."]), 422

            page = primary_model.nodes[start:count]

            if (page):
                return jsonify(**{inflect.engine().plural(primary_model.__name__.lower()):
                                  [item.serialize() for item in page]})
            else:
                return jsonify(errors=["No " + primary_model.__name__.lower() + " exists."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500

    @route("/<primary_id>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["GET"])
    @authenticate
    @authorize
    def get(self, primary_id, secondary_model_name=None, secondary_id=None):
        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")
            secondary_model = secondary_selection_field = None

            if ("secondary" in self.__model__):
                secondary_model = self.__model__.get(
                    "secondary").get(secondary_model_name)

            if ("secondary" in self.__selection_field__):
                secondary_selection_fields = self.__selection_field__.get(
                    "secondary")
                secondary_selection_field = secondary_selection_fields.get(
                    secondary_model_name)

            if (secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary")):
                return jsonify(errors=["Selected relation does not exist."]), 404

            if (primary_id):
                if (secondary_model):
                    if (secondary_id):
                        # user selected a nested model with 2 keys (from the primary and the secondary models)
                        # /users/user_id/roles/role_id -> selected role of this user
                        # /categories/cat_id/tags/tag_id -> selected tag of this category
                        primary_selected_item = primary_model.nodes.get_or_none(
                            **{primary_selection_field: str(markupsafe.escape(primary_id))})
                        if (primary_selected_item):
                            if (hasattr(primary_selected_item, secondary_model_name)):
                                related_item = getattr(
                                    primary_selected_item, secondary_model_name).get(
                                    **{secondary_selection_field: str(markupsafe.escape(secondary_id))})
                                if (related_item):
                                    return jsonify(**{inflect.engine().plural(secondary_model.__name__.lower()):
                                                      related_item.serialize()})
                                else:
                                    return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                    ) + " does not exist or the provided information is invalid."]), 404
                            else:
                                return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid."]), 404
                        else:
                            return jsonify(errors=["Selected " + primary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid."]), 404
                    else:
                        # user selected a nested model with primary key (from the primary and the secondary models)
                        # /users/user_1/roles -> all roles for this user
                        primary_selected_item = primary_model.nodes.get_or_none(
                            **{primary_selection_field: str(markupsafe.escape(primary_id))})
                        if (primary_selected_item):
                            if (hasattr(primary_selected_item, secondary_model_name)):
                                related_items = getattr(
                                    primary_selected_item, secondary_model_name).all()
                                if (related_items):
                                    return jsonify(**{inflect.engine().plural(secondary_model.__name__.lower()):
                                                      [item.serialize() for item in related_items]})
                                else:
                                    return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                    ) + " does not exist or the provided information is invalid."]), 404
                            else:
                                return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid."]), 404
                        else:
                            return jsonify(errors=["Selected " + primary_model.__name__.lower() + " does not exist or the provided information is invalid."]), 404
                else:
                    # user selected a single item (from the primary model)
                    selected_item = primary_model.nodes.get_or_none(
                        **{primary_selection_field: str(markupsafe.escape(primary_id))})

                    if (selected_item):
                        return jsonify(**{primary_model.__name__.lower(): selected_item.serialize()})
                    else:
                        return jsonify(errors=["Selected " + primary_model.__name__.lower() + " does not exist or the provided information is invalid."]), 404
            else:
                return jsonify(errors=[primary_model.__name__ + " id is not provided or is invalid."]), 404
        except DoesNotExist as e:
            self.__log.exception(e)
            return jsonify(errors=["The requested item or relation does not exist."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500

    @route("", methods=["POST"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["POST"])
    @authenticate
    @authorize
    def post(self, primary_id=None, secondary_model_name=None, secondary_id=None):
        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")
            secondary_model = secondary_selection_field = None

            # check if there exists a secondary model
            if ("secondary" in self.__model__):
                secondary_model = self.__model__.get(
                    "secondary").get(secondary_model_name)

            if ("secondary" in self.__selection_field__):
                secondary_selection_fields = self.__selection_field__.get(
                    "secondary")
                secondary_selection_field = secondary_selection_fields.get(
                    secondary_model_name)

            if (secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary")):
                return jsonify(errors=["Selected relation does not exist."]), 404

            if not (primary_id and secondary_model and secondary_id):
                # user wants to add a new item
                try:
                    # parse input data (validate or not!)
                    if (primary_model.__validation_rules__):
                        try:
                            json_data = parser.parse(
                                primary_model.__validation_rules__, request)
                        except:
                            self.__log.debug("Validation failed!")
                            return jsonify(errors=["One or more of the required fields is missing or incorrect."]), 422
                    else:
                        json_data = request.get_json(silent=True)

                    item = primary_model.nodes.get_or_none(**json_data)

                    if (not item):
                        with db.transaction:
                            item = primary_model(**json_data).save()
                            # if (primary_model == Post and g.user):
                            #     item.creator.connect(g.user)
                            #     item.save()
                            item.refresh()
                        return jsonify(**{primary_selection_field:
                                          getattr(item, primary_selection_field)})
                    else:
                        return jsonify(errors=[primary_model.__name__ + " exists!"]), 409
                except UniqueProperty:
                    return jsonify(errors=["Provided properties are not unique!"]), 409

            if (primary_id and secondary_model and secondary_id):
                # user either wants to update a relation or
                # has provided invalid information
                primary_selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(markupsafe.escape(primary_id))})

                secondary_selected_item = secondary_model.nodes.get_or_none(
                    **{secondary_selection_field: str(markupsafe.escape(secondary_id))})

                if (primary_selected_item and secondary_selected_item):
                    if (hasattr(primary_selected_item, secondary_model_name)):

                        relation = getattr(primary_selected_item,
                                           secondary_model_name)

                        related_item = secondary_selected_item in relation.all()

                        if (related_item):
                            return jsonify(errors=["Relation exists!"]), 409
                        else:
                            with db.transaction:
                                related_item = relation.connect(
                                    secondary_selected_item)
                            if (related_item):
                                return jsonify(result=["OK"])
                            else:
                                return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid."]), 404
                    else:
                        return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid."]), 404
                else:
                    return jsonify(errors=["Selected " + primary_model.__name__.lower(
                    ) + " does not exist or the provided information is invalid."]), 404

            return jsonify(errors=["Invalid information provided."]), 404
        except DoesNotExist as e:
            self.__log.exception(e)
            return jsonify(errors=["The requested item or relation does not exist."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500

    @route("/<primary_id>", methods=["PUT"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["PUT"])
    @authenticate
    @authorize
    # @db.transaction
    def put(self, primary_id, secondary_model_name=None, secondary_id=None):
        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")
            secondary_model = secondary_selection_field = None

            # check if there exists a secondary model
            if ("secondary" in self.__model__):
                secondary_model = self.__model__.get(
                    "secondary").get(secondary_model_name)

            if ("secondary" in self.__selection_field__):
                secondary_selection_fields = self.__selection_field__.get(
                    "secondary")
                secondary_selection_field = secondary_selection_fields.get(
                    secondary_model_name)

            if (secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary")):
                return jsonify(errors=["Selected relation does not exist."]), 404

            if (primary_id and secondary_model_name is None and secondary_id is None):
                # a single item is going to be updated(/replaced) with the
                # provided JSON data
                selected_item = primary_model.nodes.get_or_none(
                    **{primary_id: str(markupsafe.escape(primary_id))})

                if (selected_item):
                    # parse input data (validate or not!)
                    if (primary_model.__validation_rules__):
                        try:
                            json_data = parser.parse(
                                primary_model.__validation_rules__, request)
                        except:
                            self.__log.debug("Validation failed!")
                            return jsonify(errors=["One or more of the required fields is missing or incorrect."]), 422
                    else:
                        json_data = request.get_json(silent=True)

                    if (json_data):
                        with db.transaction:
                            # delete and create a new one
                            selected_item.delete()  # delete old node and its relations
                            created_item = primary_model(
                                **json_data).save()  # create a new node

                            if (created_item):
                                # if (self.__model__ == Post and g.user):
                                #     created_item.creator.connect(g.user)
                                #     created_item.save()
                                created_item.refresh()
                                return jsonify(**{primary_selection_field:
                                                  getattr(created_item, primary_selection_field)})
                            else:
                                return jsonify(errors=["There was an error creating your desired item."]), 500
                    else:
                        return jsonify(errors=["Invalid information provided."]), 404
                else:
                    return jsonify(errors=[primary_model.__name__ + " does not exist."]), 404
            else:
                if (primary_id, secondary_model_name, secondary_id):
                    # user either wants to update a relation or
                    # has provided invalid information
                    primary_selected_item = primary_model.nodes.get_or_none(
                        **{primary_selection_field: str(markupsafe.escape(primary_id))})

                    secondary_selected_item = secondary_model.nodes.get_or_none(
                        **{secondary_selection_field: str(markupsafe.escape(secondary_id))})

                    if (primary_selected_item and secondary_selected_item):
                        if (hasattr(primary_selected_item, secondary_model_name)):

                            relation = getattr(primary_selected_item,
                                               secondary_model_name)

                            all_relations = relation.all()

                            related_item = None

                            with db.transaction:
                                # remove all relationships
                                for each_relation in all_relations:
                                    relation.disconnect(each_relation)

                                # add a new relationship
                                related_item = relation.connect(
                                    secondary_selected_item)

                            if (related_item):
                                return jsonify(result=["OK"])
                            else:
                                return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                                ) + " does not exist or the provided information is invalid."]), 404
                        else:
                            return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid."]), 404
                    else:
                        return jsonify(errors=["One of the selected models does not exist or the provided information is invalid."]), 404

                return jsonify(errors=["Invalid information provided."]), 404
        except DoesNotExist as e:
            self.__log.exception(e)
            return jsonify(errors=["The requested item or relation does not exist."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500

    @authenticate
    @authorize
    def patch(self, primary_id):
        """Partially update a model. Note: updating
        relations via PATCH is not supported."""
        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")

            if (primary_model.__validation_rules__):
                try:
                    json_data = parser.parse(
                        primary_model.__validation_rules__, request)
                except:
                    self.__log.debug("Validation failed!")
                    return jsonify(errors=["One or more of the required fields is missing or incorrect."]), 422
            else:
                json_data = request.get_json(silent=True)

            if (primary_id):
                selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(markupsafe.escape(primary_id))})

                if (selected_item):
                    # FIXME: validate all input (JSON) data
                    if (json_data):
                        updated_item = None
                        with db.transaction:
                            selected_item.__dict__.update(json_data)
                            updated_item = selected_item.save()
                            selected_item.refresh()

                        if (updated_item):
                            return jsonify(result="OK")
                        else:
                            return jsonify(errors=["There was an error updating your desired item."]), 500
                    else:
                        return jsonify(errors=["Invalid information provided."]), 404
                else:
                    return jsonify(errors=["Item does not exist."]), 404
            else:
                return jsonify(errors=[primary_model.__name__ + " id is not provided or is invalid."]), 404
        except DoesNotExist as e:
            self.__log.exception(e)
            return jsonify(errors=["The requested item or relation does not exist."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500

    @route("/<primary_id>", methods=["DELETE"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["DELETE"])
    @authenticate
    @authorize
    def delete(self, primary_id, secondary_model_name=None, secondary_id=None):
        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")
            secondary_model = secondary_selection_field = None

            # check if there exists a secondary model
            if ("secondary" in self.__model__):
                secondary_model = self.__model__.get(
                    "secondary").get(secondary_model_name)

            if ("secondary" in self.__selection_field__):
                secondary_selection_fields = self.__selection_field__.get(
                    "secondary")
                secondary_selection_field = secondary_selection_fields.get(
                    secondary_model_name)

            if (secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary")):
                return jsonify(errors=["Selected relation does not exist."]), 404

            if (primary_id and secondary_model_name is None and secondary_id is None):
                selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(markupsafe.escape(primary_id))})

                if (selected_item):
                    is_deleted = False
                    with db.transaction:
                        is_deleted = selected_item.delete()

                    if (is_deleted):
                        return jsonify(result="OK")
                    else:
                        return jsonify(errors=["There was an error deleting the item."]), 500
                else:
                    return jsonify(errors=["Item does not exist."]), 404
            else:
                if (primary_id, secondary_model_name, secondary_id):
                    # user either wants to update a relation or
                    # has provided invalid information
                    primary_selected_item = primary_model.nodes.get_or_none(
                        **{primary_selection_field: str(markupsafe.escape(primary_id))})

                    secondary_selected_item = secondary_model.nodes.get_or_none(
                        **{secondary_selection_field: str(markupsafe.escape(secondary_id))})

                    if (primary_selected_item and secondary_selected_item):
                        if (hasattr(primary_selected_item, secondary_model_name)):

                            relation = getattr(primary_selected_item,
                                               secondary_model_name)

                            related_item = secondary_selected_item in relation.all()

                            if (not related_item):
                                return jsonify(errors=["Relation does not exist!"]), 409
                            else:
                                with db.transaction:
                                    relation.disconnect(
                                        secondary_selected_item)

                                if (secondary_selected_item not in relation.all()):
                                    return jsonify(result=["OK"])
                                else:
                                    return jsonify(errors=["There was an error removing the selected relation."]), 500
                        else:
                            return jsonify(errors=["Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid."]), 404
                    else:
                        return jsonify(errors=["Selected " + primary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid."]), 404
                return jsonify(errors=[primary_model.__name__ + " id is not provided or is invalid."]), 404
        except DoesNotExist as e:
            self.__log.exception(e)
            return jsonify(errors=["The requested item or relation does not exist."]), 404
        except Exception as e:
            self.__log.exception(e)
            return jsonify(errors=["An error occurred while processing your request."]), 500
