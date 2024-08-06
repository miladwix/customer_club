from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Transaction


@registry.register_document
class TransactionTestDocument(Document):
    customer = fields.ObjectField(attr='customer', properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'email': fields.TextField(),
    })

    amount = fields.DoubleField(
        attr="amount",
        fields={
            "suggest": fields.Completion(),
        },
    )

    date = fields.DateField(
        attr='date',
        fields={
            'suggest': fields.Completion(),
        }
    )

    class Index:
        name = 'test_transactions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Transaction
        fields = [
            'id',
            'description'
        ]