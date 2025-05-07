from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Profile
from core.tasks import generate_thumbnails

@receiver(post_save, sender=Profile)
def profile_avatar_post_save(sender, instance, **kwargs):
    if instance.avatar:
        # имя модели в Django-формате "app_label.ModelName"
        generate_thumbnails.delay('core.Profile', instance.pk, 'avatar')
