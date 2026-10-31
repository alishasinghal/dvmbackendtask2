def user_roles(request):
    names = set()
    if request.user.is_authenticated:
        names = set(request.user.groups.values_list("name", flat=True))
    return {
        "is_customer": "Customer" in names,
        "is_organization": "Organization" in names,
    }