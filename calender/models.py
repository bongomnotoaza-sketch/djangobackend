from django.db import models

# Create your models here.
from django.db import models

class Assinments(models.Model):
    
    id = models.BigIntegerField()
    
    subject = models.CharField(
        max_length=20,
        )
    
    taskdescription = models.CharField(max_length=20,)
    due_date = models.DateTimeField()
    
class Lessons(models.Model):
    id = models.BigIntegerField()
    
    subject = models.CharField(max_length=20,)
    lessontime = models.TimeField()
    
