from django.shortcuts import render
from django.views import View

# Create your views here.
class ManagementView(View):
    __template_name = 'pages/management.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Management'
        }
        return render(request=request, template_name=self.__template_name, context=context)
