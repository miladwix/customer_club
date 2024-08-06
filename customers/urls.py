from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet,
    CustomerSearchApiView,
    TransactionViewSet,
    TransactionSearchView)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [path("customers/search/", CustomerSearchApiView.as_view()),
               path('transactions/search/', TransactionSearchView.as_view({'get': 'list'}),
                    name='transaction-search'),
               path('customers/<int:customer_id>/transactions/',
                    TransactionViewSet.as_view({'post': 'create'}), name='customer-create-transaction'),
               ]

urlpatterns += router.urls
