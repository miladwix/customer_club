from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class TimeFields(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        abstract = True


class Customer(TimeFields):
    name = models.CharField("Name", max_length=32)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Phone", max_length=20)
    loyalty_score = models.IntegerField("Loyalty Score", default=0)
    objects = SoftDeleteManager()  # Manager for active records
    all_objects = models.Manager()  # Manager for all records, including soft-deleted

    def delete(self,  *args, **kwargs):
        """Mark the instance and related transactions as deleted."""
        self.deleted_at = timezone.now()
        self.save()
        self.transactions.all().update(deleted_at=self.deleted_at)

    def restore(self):
        """Restore a soft-deleted instance and its related transactions."""
        self.deleted_at = None
        self.save()
        self.transactions.all().update(deleted_at=None)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField("Amount", max_digits=10, decimal_places=2)
    description = models.TextField("Description", null=True, blank=True)
    date = models.DateTimeField("Date", default=timezone.now)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True)
    objects = SoftDeleteManager()  # Manager for active records
    all_objects = models.Manager()  # Manager for all records, including soft-deleted

    def __str__(self):
        return f"{self.customer.name} - {self.amount}"

    def delete(self, *args, **kwargs):
        """Mark the instance as deleted."""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted instance."""
        self.deleted_at = None
        self.save()
