from rest_framework.viewsets import (
    ModelViewSet, 
    GenericViewSet)
from rest_framework.mixins import (
    ListModelMixin, 
    CreateModelMixin, 
    RetrieveModelMixin)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from elasticsearch_dsl import Q
from django_elasticsearch_dsl_drf.filter_backends import (
    SearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django.core.cache import cache
from .models import (
    Customer, 
    Transaction)
from .serializers import (
    CustomerSerializer,
    CustomerDocumentSerializer,
    TransactionSerializer,
    TransactionDocumentSerializer)
from .documents import CustomerDocument
from .documents import TransactionDocument
from .signals import update_customer_loyalty_score


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'customers_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes

        return response

    def retrieve(self, request, *args, **kwargs):
        cache_key = f'customer_{kwargs["pk"]}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes

        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete('customers_list')  # Invalidate list cache
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete('customers_list')  # Invalidate list cache
        cache.delete(f'customer_{kwargs["pk"]}')  # Invalidate detail cache
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.delete('customers_list')  # Invalidate list cache
        cache.delete(f'customer_{kwargs["pk"]}')  # Invalidate detail cache
        return response


class CustomerSearchApiView(APIView):
    serializer_class = CustomerDocumentSerializer
    document_class = CustomerDocument

    def generate_q_expression(self, query):
        return Q('multi_match', query=query, fields=['name', 'email'])

    def get(self, request):
        query = self.request.query_params.get('query')
        if not query:
            return Response({'error': 'No query parameter provided.'}, status=status.HTTP_400_BAD_REQUEST)
        q = self.generate_q_expression(query)
        search = self.document_class.search().query(q)
        serializer = self.serializer_class(search.to_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionViewSet(GenericViewSet,
                         ListModelMixin,
                         CreateModelMixin,
                         RetrieveModelMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'transactions_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes

        return response

    def retrieve(self, request, *args, **kwargs):
        cache_key = f'transaction_{kwargs["pk"]}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes

        return response

    def create(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'detail': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['customer'] = customer.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cache.delete('transactions_list')  # Invalidate list cache
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TransactionSearchView(DocumentViewSet):
    document = TransactionDocument
    serializer_class = TransactionDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
    ]

    filter_fields = {
        'amount': 'amount',
        'date': 'date',
    }

    search_fields = {
        'amount': {'boost': 2},
        'date': {'boost': 2},
    }

    ordering_fields = {
        'amount': 'amount',
        'date': 'date',
    }

    ordering = 'date'
