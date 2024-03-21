from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
   
    id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True)
    datasheet_file_path = models.FileField(max_length=255, upload_to='admin_datasheet/', null=True,   blank=True)
    username = models.CharField(max_length=20, default="admin")
    rating = models.IntegerField(default=0)
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.DecimalField(default=0, max_digits=3, decimal_places=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name + ' ' + self.sku
        else:
            return f"Product {self.id}"
        
def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/dataset/<filename>
    return f'user_uploads/user_{instance.username.username}/{filename}'

class Listing(models.Model):
   
    id = models.AutoField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset_name = models.CharField(max_length=255, blank=True)
    dataset_description = models.TextField(blank=True)
    dataset_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dataset_image = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)
    dataset_file_path = models.FileField(max_length=255, upload_to=user_directory_path, null=True)
    datasheet_file_path = models.FileField(max_length=255, upload_to=user_directory_path, null=True, blank=True)
    rating = models.IntegerField(default=0)
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.DecimalField(default=0, max_digits=3, decimal_places=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
             return self.username.username + ' added ' + self.dataset_name
    
