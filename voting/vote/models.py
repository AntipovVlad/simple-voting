from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
# Create your models here.


class Voting(models.Model):
    question = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    count = models.CharField(max_length=250, default="0", null=True)
    vote_type = models.IntegerField(default=0, null=False)


class Option(models.Model):
    voting = models.CharField(max_length=250, default="0", null=True)
    text = models.CharField(max_length=50)


class UserData(models.Model):
    bio = models.CharField(max_length=250,  default="none", null=False)
    answered = models.IntegerField(default=0, null=False)
    pic_url = models.CharField(max_length=250,  default="none", null=False)


class MegaData(models.Model):
    user = models.IntegerField(default=0, null=False)
    question = models.IntegerField(default=0, null=False)
    answer = models.IntegerField(default=0, null=False)

