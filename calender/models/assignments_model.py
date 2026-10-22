from django.db import models

class Assinments(models.Model):
    
    id = models.BigIntegerField()
    
    subject = models.models.CharField(
        max_length=20,
        )
    
    taskdescription = models.CharField(max_length=20,)
    due_date = models.DateTimeField()