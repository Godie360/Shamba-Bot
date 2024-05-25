from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Message(models.Model):

    message = models.TextField()
    is_user = models.BooleanField(default=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars', null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField
    
    def __str__(self):
        return str(self.user)