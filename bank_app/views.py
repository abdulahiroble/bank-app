from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Customer, Account, Loan, Transaction
from .forms import CustomerForm, AccountForm

from django.views.generic import TemplateView
from django.db.models import Count

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

class IndexView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_customers'] = Customer.objects.all().count()
        context['num_accounts'] = Account.objects.all().count()
        context['num_loans'] = Loan.objects.all().count()
        return context

# class IndexView(LoginRequiredMixin, View):
#     login_url = 'login'

#     def get(self, request):
#         num_customers = Customer.objects.all().count()
#         num_accounts = Account.objects.all().count()
#         num_loans = Loan.objects.all().count()

#         context = {
#             'num_customers': num_customers,
#             'num_accounts': num_accounts,
#             'num_loans': num_loans,
#         }

#         return render(request, 'bank_app/base.html', context)


class CustomerListView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        customers = Customer.objects.all()
        return render(request, 'bank_app/customer_list.html', {'customers': customers})


class CreateCustomerView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Customer
    form_class = CustomerForm
    template_name = 'bank_app/create_customer.html'
    success_url = reverse_lazy('customer_list')


class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Customer
    form_class = CustomerForm
    template_name = 'bank_app/update_customer.html'
    success_url = reverse_lazy('customer_list')


class DeleteCustomerView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Customer
    template_name = 'bank_app/delete_customer.html'
    success_url = reverse_lazy('customer_list')


class ChangeCustomerRankView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        customer = Customer.objects.get(pk=pk)
        return render(request, 'bank_app/change_customer_rank.html', {'customer': customer})

    def post(self, request, pk):
        customer = Customer.objects.get(pk=pk)
        new_rank = request.POST.get('new_rank')

        if new_rank not in dict(Customer.RANK_CHOICES).keys():
            messages.error(request, f"Invalid rank '{new_rank}'.")
        else:
            customer.rank = new_rank
            customer.save()
            messages.success(request, f"Rank for customer '{customer}' updated to '{new_rank}'.")
            return redirect('customer_list')

        return render(request, 'bank_app/change_customer_rank.html', {'customer': customer})


class AccountListView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        accounts = Account.objects.all()
        return render(request, 'bank_app/account_list.html', {'accounts': accounts})


class AccountDetailsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, account_number):
        account = Account.objects.get(account_number=account_number)
        transactions = Transaction.objects.filter(account=account).order_by('-date')
        return render(request, 'bank_app/account_details.html', {'account': account, 'transactions': transactions})


class CreateAccountView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Account
    form_class = AccountForm
    template_name = 'bank_app/create_account.html'
    success_url = reverse_lazy('account_list')
    
class LogoutView(LogoutView):
    template_name = 'registration/logout.html'
    next_page = reverse_lazy('home')
    
class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')
    
    
class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')


# def test(request):
#     return render(request, 'registration/register.html')