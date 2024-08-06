from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction


@receiver(post_save, sender=Transaction)
def update_customer_loyalty_score(sender, instance, created, **kwargs):
    if created:
        # Update the customer's loyalty score based on the count of transactions
        instance.customer.loyalty_score += 1
        instance.customer.save()
