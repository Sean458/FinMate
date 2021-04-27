from django.db import models
from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone

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
    feedback = models.TextField()
    description = models.TextField()
    sentiment = models.FloatField(default=0.0)


class CustomUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,)
    country = models.CharField(max_length=30)
    credit_score = models.FloatField(default=0.0)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
