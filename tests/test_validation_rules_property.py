from neomodel import *
from webargs import fields
import grest


class model(StructuredNode, grest.utils.Node):
    GREEK = (
        ("A", "Alpha"),
        ("B", "Beta"),
        ("G", "Gamma")
    )

    uuid = UniqueIdProperty()
    string = StringProperty(required=True)
    choices = StringProperty(choices=GREEK)
    integer = IntegerProperty()
    json = JSONProperty()
    array_of_string = ArrayProperty(StringProperty())
    raw_data = ArrayProperty()
    date = DateProperty()
    datetime = DateTimeProperty()
    boolean = BooleanProperty()
    email = EmailProperty()


def test_validation_rules_property():
    instance = model()

    for rule in instance.__validation_rules__.items():
        assert isinstance(rule[1], fields.Field)
        if isinstance(rule[1], fields.List):
            assert isinstance(rule[1].container, fields.Field)
