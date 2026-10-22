from django.db import models


class Quantity(models.Model):
    id = models.AutoField(primary_key=True)
    quantity_name = models.CharField(max_length=100)

    def __str__(self):
        return self.quantity_name