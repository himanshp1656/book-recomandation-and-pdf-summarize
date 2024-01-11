from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genre = models.CharField(max_length=100, null=True)
    favorite_author = models.CharField(max_length=100, null=True)
    favorite_book = models.CharField(max_length=100, null=True)
    

    def __str__(self):
        return self.user.username

class bookdetails(models.Model):
    genre = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    

    def __str__(self):
        return self.title
