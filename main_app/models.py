from django.db import models

# Create your models here.           
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/', default="", blank=True)
    file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.name:
            return self.name + ' ' + self.sku
        else:
            return f"Product {self.id}"
