from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import (
    Customer,
    Transaction)


@registry.register_document
class CustomerDocument(Document):
    name = fields.TextField(
        fields={
            'raw': fields.KeywordField()
        }
    )

    email = fields.TextField(
        fields={
            'raw': fields.KeywordField()
        }
    )

    class Index:
        name = 'customers'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Customer
        fields = [
            'id',
            'phone',
            'loyalty_score',
            'created_at',
            'updated_at',
            'deleted_at',
        ]


@registry.register_document
class TransactionDocument(Document):
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
        name = 'transactions'
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
