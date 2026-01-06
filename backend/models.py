from django.db import models

# Create your models here.
from django.db import models


class Diccionario(models.Model):
    palabra = models.CharField(max_length=100)

    def __str__(self):
        return self.palabra