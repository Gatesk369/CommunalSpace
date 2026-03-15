from django.db import models

# Create your models here.
class Space(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField()
    location_type=models.CharField(max_length=50)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name