from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    group_name = None

    def test_func(self):
        return self.request.user.groups.filter(name=self.group_name).exists()
class OrganizationRequiredMixin(GroupRequiredMixin):
    group_name = "Organization"

    def test_func(self):
        return super().test_func() and hasattr(self.request.user, "organization")
