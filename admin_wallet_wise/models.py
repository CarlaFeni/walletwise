from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Representacion de una tabla en la BD

class walletWise(models.Model):
    nombre = models.CharField(max_length=50)
    alias = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)


class Movimiento(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ahorro', 'Ahorro'),
        ('inversion', 'Inversión'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    #nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo}: {self.monto}"

