from django.db import models

# Create your models here.
class user(models.Model):
    First_name=models.CharField(max_length=50)
    Last_name=models.CharField(max_length=50)
    username=models.CharField(primary_key=True, max_length=50)
    password=models.CharField(max_length=50)
    action=models.IntegerField()
    adventure=models.IntegerField()
    romantic=models.IntegerField()
    horror=models.IntegerField()
    mystery=models.IntegerField()
    scifi=models.IntegerField()
    comedy=models.IntegerField()
    desc=models.CharField(max_length=500)
    likedmovies = models.TextField(null=True)
    def __str__(self):
        return self.First_name
