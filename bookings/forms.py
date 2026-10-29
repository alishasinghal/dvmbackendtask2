from decimal import Decimal

from django import forms


class AddMoneyForm(forms.Form):
    amount = forms.DecimalField(
        min_value=Decimal("1"), max_value=Decimal("100000"),
        max_digits=8, decimal_places=2,
    )


class BookingForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10)