from django.db import models

class TypeProduct(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'

class Products(models.Model):
    Tittle = models.CharField(max_length=40)
    Description = models.CharField(max_length=200)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Image = models.ImageField()
    Type = models.ForeignKey(TypeProduct , on_delete=models.CASCADE , default='')

    def __str__(self):
        return f"{self.Tittle} | {str(self.Price)}$"

    class Meta:
        verbose_name_plural = "Products"