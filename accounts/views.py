from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.groups.add(Group.objects.get(name="Customer"))
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def home(request):
    if request.user.groups.filter(name="Customer").exists():
        return redirect("event_list")
    if request.user.groups.filter(name="Organization").exists():
        return redirect("org_dashboard")
    return render(request, "home.html")