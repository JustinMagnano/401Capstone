import random
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock

'''@receiver(post_save, sender=Stock)
def update_stock_price(sender, instance, created, **kwargs):
    current_time = datetime.now()
    time_diff = current_time - instance.priceTime
    diff_min = time_diff.total_seconds() / 60

    # Update price if more than 1 minute has passed (or adjust as needed)
    if diff_min >= 1:  
        random_number = random.uniform(-0.15, 0.15)
        instance.price += (instance.price * random_number)

        # Update min and max prices
        if instance.minPrice is None or instance.price < instance.minPrice:
            instance.minPrice = instance.price
        if instance.maxPrice is None or instance.price > instance.maxPrice:
            instance.maxPrice = instance.price

        # Update the priceTime to the current time
        instance.priceTime = current_time
        
        # Save the instance with updated values
        instance.save()'''
