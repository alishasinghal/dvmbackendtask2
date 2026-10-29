from django import forms
from django.utils import timezone

from events.models import Slot


class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ["start_time", "end_time", "price", "capacity"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after the start time.")
        if start and start <= timezone.now():
            raise forms.ValidationError("The slot must start in the future.")
        return cleaned

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise forms.ValidationError("Capacity must be at least 1.")
        return capacity