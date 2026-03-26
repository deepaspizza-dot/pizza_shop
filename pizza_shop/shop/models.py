from django.db import models

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    small_price = models.IntegerField()
    medium_price = models.IntegerField()
    large_price = models.IntegerField()

    image = models.ImageField(upload_to='pizzas/')

    def __str__(self):
        return self.name
    
class Order(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)

    size = models.CharField(max_length=20)
    quantity = models.IntegerField()

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_price = models.IntegerField()

    status = models.CharField(
    max_length=20,
    default='Pending'
)

    is_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
# Create your models here.
