from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Add any user-related signals here if needed
# For example, you might want to create a user profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # You can add any initialization code here
        pass 