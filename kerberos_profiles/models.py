from django.db import models

# Create your models here.
class Profile(models.Model):
    kerberosID = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.CharField(max_length=50, null=False)
    uniqueiitdid = models.CharField(max_length=50, null=False)
    category = models.CharField(max_length=50, null=False)
    department = models.CharField(max_length=50, null=False)
    deviceUUID = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f'{self.kerberosID} - {self.name} - {self.category}'
