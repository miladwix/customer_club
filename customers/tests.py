from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from .models import Customer, Transaction


class CustomerViewSetTestCase(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name='milad',
            email='milad.mohammadian@gamil.com',
            phone='09382061246',
        )
        self.list_url = reverse('customers-list')
        self.detail_url = reverse('customers-detail', args=[self.customer.id])

    def tearDown(self):
        cache.clear()

    def test_list_customers(self):
        # Initial request should fetch from the database and cache the response
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

        # Ensure the response data is cached
        cached_data = cache.get('customers_list')
        self.assertIsNotNone(cached_data)

        # Subsequent request should fetch from the cache
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_customer(self):
        # Initial request should fetch from the database and cache the response
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), 'milad')

        # Ensure the response data is cached
        cached_data = cache.get(f'customer_{self.customer.id}')
        self.assertIsNotNone(cached_data)

        # Subsequent request should fetch from the cache
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_customer(self):
        data = {
            "name": "mehrdad",
            "email": "mehrdad.azad@gamil.com",
            "phone": "09382061246",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

        # Ensure the cache for the customer list is invalidated
        cache_data = cache.get('customers_list')
        self.assertIsNone(cache_data)

    def test_update_customer(self):
        data = {
            "name": "mehrdad",
            "email": "mehrdad.azad@gamil.com",
            "phone": "09382061246",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'mehrdad')

        # Ensure the cache for the specific customer and the list is invalidated
        cache_data = cache.get(f'customer_{self.customer.id}')
        self.assertIsNone(cache_data)
        cache_data = cache.get('customers_list')
        self.assertIsNone(cache_data)

    def test_delete_customer(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

        # Ensure the cache for the specific customer and the list is invalidated
        cache_data = cache.get(f'customer_{self.customer.id}')
        self.assertIsNone(cache_data)
        cache_data = cache.get('customers_list')
        self.assertIsNone(cache_data)


class TransactionViewSetTestCase(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name='milad',
            email='milad.mohammadian@gamil.com',
            phone='09382061246',
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            amount=110000.00,
            description='Test transaction'
        )
        self.list_url = reverse('transactions-list')
        self.detail_url = reverse('transactions-detail', args=[self.transaction.id])
        self.create_url = reverse('customer-create-transaction', args=[self.customer.id])

    def tearDown(self):
        cache.clear()

    def test_list_transactions(self):
        # Initial request should fetch from the database and cache the response
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

        # Ensure the response data is cached
        cached_data = cache.get('transactions_list')
        self.assertIsNotNone(cached_data)

        # Subsequent request should fetch from the cache
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_transaction(self):
        # Initial request should fetch from the database and cache the response
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('amount'), '110000.00')

        # Ensure the response data is cached
        cached_data = cache.get(f'transaction_{self.transaction.id}')
        self.assertIsNotNone(cached_data)

        # Subsequent request should fetch from the cache
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_transaction(self):
        data = {
            "amount": "50000.00",
            "description": "New transaction"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

        # Ensure the cache for the transaction list is invalidated
        cache_data = cache.get('transactions_list')
        self.assertIsNone(cache_data)

    def test_cache_invalidation_on_create(self):
        # Ensure the cache is populated initially
        self.client.get(self.list_url)
        cached_data = cache.get('transactions_list')
        self.assertIsNotNone(cached_data)

        # Create a new transaction
        data = {
            "amount": "75.00",
            "description": "Another transaction"
        }
        self.client.post(self.create_url, data)

        # Ensure the cache for the transaction list is invalidated
        cache_data = cache.get('transactions_list')
        self.assertIsNone(cache_data)



