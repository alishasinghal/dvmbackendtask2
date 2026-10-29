from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import Wallet, OrganizationProfile


@receiver(post_save, sender=get_user_model())
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
@receiver(post_save, sender=OrganizationProfile)
def add_to_organization_group(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name="Organization")
        instance.user.groups.add(group)