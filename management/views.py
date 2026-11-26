from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class ManagementAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return any((
            getattr(user, 'is_admin', False),
            getattr(user, 'is_manager', False),
            getattr(user, 'is_receptionist', False),
        ))


class ManagementView(ManagementAccessMixin, View):
    template_name = 'pages/management.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Management',
            'active_nav_item': 'nav-management',
        }
        return render(request=request, template_name=self.template_name, context=context)
