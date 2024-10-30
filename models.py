from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    rating = models.FloatField()  # Assuming rating is a float
    location = models.CharField(max_length=255)
    distance = models.FloatField()
    types = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    website = models.URLField(blank=True)
    favorite = models.BooleanField(default=False)
    reviews = models.CharField(max_length=255, default="No reviews yet")

    def __str__(self):
        return self.name

class Review(models.Model):
    review = models.TextField(default="")
    rating = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)


class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   favorites = models.ManyToManyField(Restaurant, blank=True)
   reviews = models.ManyToManyField(Review, blank=True)
   security_answer = models.CharField(max_length=255, blank=True)


   def __str__(self):
       return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
   if created:
       Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
   instance.profile.save()
