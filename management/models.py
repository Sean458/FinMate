from django.db import models
from django.contrib.auth.models import AnonymousUser, User

# Create your models here.


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)
    is_expense = models.BooleanField()

    def __str__(self):
        return "(" + str(self.id) + ") " + self.category_name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()
