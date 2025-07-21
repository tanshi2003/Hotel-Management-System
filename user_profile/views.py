from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from user_profile.models import Person, Account, Address
from user_profile.forms import PersonForm, AccountForm, AddressForm, PersonForm2


# Create your views here.
class RegisterView(View):
    template_name = 'user/register.html'
    __homepage_url_name = 'home'
    person_role = {
        'admin':False,
        'manager': False,
        'receptionist': False,
        'guest': False,
        'staff': False
    }

    def get(self, request, *args, **kwargs):
        person_form = PersonForm()
        account_form = AccountForm()
        
        context = {
            'title': 'User Registration',
            'active_nav_item': 'nav-signup',
            'person_form': person_form,
            'account_form': account_form
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        person_form = PersonForm(request.POST)
        account_form = AccountForm(request.POST)
        if person_form.is_valid() and account_form.is_valid():
            print('form is valid')
            person = person_form.save()
            # self.person_role[person.account_type] = True
            account = Account(
                email=person.email,
                # is_admin = self.person_role['admin'],
                # is_manager = self.person_role['manager'],
                # is_receptionist = self.person_role['receptionist'],
                # is_guest = self.person_role['guest'],
                # is_staff = self.person_role['staff'],
                person=person
            )
            account.set_password(account_form.cleaned_data.get("password"))
            account.save()
            return redirect(self.__homepage_url_name)
        else:
            print("Form not valid")
            context = {
                'title': 'User Registration',
                'active_nav_item': 'nav-signup',
                'person_form': person_form,
                'account_form': account_form
            }
            return render(request, self.template_name, context=context)


class LoginView(View):
    __template_name = 'user/login.html'
    __homepage_url_name = 'home'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # User already logged in
            return redirect(self.__homepage_url_name)

         # User not logged in
        person_form = PersonForm()
        account_form = AccountForm()
        context = {
            'title': 'User Login',
            'active_nav_item': 'nav-signin',
            'person_form': person_form,
            'account_form': account_form
        }
        return render(request, self.__template_name, context=context)
    
    def post(self, request, *args, **kwargs):

        account_form = AccountForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(self.__homepage_url_name)
        else:
            person_form = PersonForm()
            account_form = AccountForm()
            context = {
                'title': 'User Login',
                'active_nav_item': 'nav-signin',
                'person_form': person_form,
                'account_form': account_form,
                'error_msg': "Login failed!"
            }
            return render(request, self.__template_name, context=context)


class LogoutView(View):
    __homepage_url_name = 'home'

    def get(self, request, *args, **kwargs):
        """ Loged out the user """
        logout(request)
        return redirect(self.__homepage_url_name)


class ProfileView(LoginRequiredMixin, View):
    __template_name = 'user/profile.html'

    def get(self, request, *args, **kwargs):
        
        person = Person.objects.get(email=request.user.email)
        person_form = PersonForm2(instance=person)
        try:
            address_form = AddressForm(instance=person.address)
        except ObjectDoesNotExist:
            address_form = AddressForm()
        context = {
            'title': 'User Profile',
            'active_nav_item': 'nav-user',
            'person_form': person_form,
            'address_form': address_form
        }
        return render(request=request, template_name=self.__template_name, context=context)


    def post(self, request, *args, **kwargs):
        person = Person.objects.get(email=request.user.email)
        person_form=PersonForm2(request.POST, instance=person)
        is_empty_address = None
        try:
            address_form = AddressForm(request.POST or None, instance=person.address)
        except ObjectDoesNotExist:
            address_form = AddressForm(request.POST)
            is_empty_address=True
        

        if person_form.is_valid() and address_form.is_valid():
            if is_empty_address:
                address = Address(
                    city=address_form.cleaned_data['city'],
                    country=address_form.cleaned_data['country'],
                    zip_code=address_form.cleaned_data['zip_code'],
                    person=person,
                )
                person_form.save()
                address.save()
            else:
                person_form.save()
                address_form.save()
            return redirect('user_profile:profile')

        context = {
            'title': 'User Profile',
            'active_nav_item': 'nav-user',
            'person_form': person_form,
            'address_form': address_form,
            'error_msg': "Changes not saved!"
        }
        return render(request=request, template_name=self.__template_name, context=context)