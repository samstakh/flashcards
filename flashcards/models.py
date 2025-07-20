import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone


import uuid

def generate_share_token():
    return str(uuid.uuid4())



# Create your models here.
class User(AbstractUser):
    pass


class Deck(models.Model):
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    share_token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_on = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_share_url(self):
        return reverse('shared_deck_view', args=[self.share_token])

    



# study session that logs when user reviews a deck
class FlashcardSession(models.Model):
    
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    reviewed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s session on {self.deck.name} at {self.reviewed_on.strftime('%Y-%m-%d %H:%M')}"


# single card in deck
class Card(models.Model):
   
    deck = models.ForeignKey(Deck, models.CASCADE, related_name="card")
    front = models.TextField()
    back = models.TextField()
    last_reviewed = models.DateTimeField(null=True, blank=True)


    # difficulty of card
    difficulty = models.CharField(max_length=20, choices=[
        ('again', 'Again'),
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.front[:50]