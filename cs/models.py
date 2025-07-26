# chat/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Chat(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat #{self.id} - {self.customer.username}"
    
    def get_absolute_url(self):
        return reverse('cs:chat_detail', kwargs={'chat_id': self.id})

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messagesf')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} at {self.timestamp}"
