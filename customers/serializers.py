from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .models import (
    Customer,
    Transaction)
from .documents import (
    CustomerDocument,
    TransactionDocument)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'loyalty_score', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomerDocumentSerializer(DocumentSerializer):
    class Meta:
        document = CustomerDocument
        fields = ['id', 'name', 'email', 'phone', 'loyalty_score',]


class TransactionSerializer(serializers.ModelSerializer):

    customer_info = CustomerSerializer(source='customer', read_only=True, required=False)

    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'amount', 'description', 'customer_info', 'date']
        read_only_fields = ['date', 'customer_info']


class TransactionDocumentSerializer(DocumentSerializer):
    class Meta:
        document = TransactionDocument
        fields = ['id', 'amount', 'date', 'description', 'customer']
