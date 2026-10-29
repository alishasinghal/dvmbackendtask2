from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0), name="wallet_balance_non_negative"
            )
        ]
    def __str__(self):
        return f"{self.user.username}: {self.balance}"


class OrganizationProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name