from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Customer, Account, Loan, Transaction, Payment
from .forms import CustomerForm, AccountForm, LoanForm, PaymentForm

from django.views.generic import TemplateView, ListView

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework import status
from .models import Loan
from .serializers import LoanSerializer, AccountSerializer


class IndexView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_customers'] = Customer.objects.all().count()
        context['num_accounts'] = Account.objects.all().count()
        context['num_loans'] = Loan.objects.all().count()
        return context

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'bank_app/customer_list.html'
    login_url = 'login'


class CreateCustomerView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Customer
    form_class = CustomerForm
    template_name = 'bank_app/create_customer.html'
    success_url = reverse_lazy('bank_app/customer_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


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


# class AccountDetailsView(LoginRequiredMixin, View):
#     login_url = 'login'

#     def get(self, request, account_number):
#         account = Account.objects.get(account_number=account_number)
#         transactions = Transaction.objects.filter(account=account).order_by('-date')
#         return render(request, 'bank_app/account_details.html', {'account': account, 'transactions': transactions})


class CreateAccountView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Account
    form_class = AccountForm
    template_name = 'bank_app/create_account.html'
    success_url = reverse_lazy('bank_app:home')


class CreateLoanView(View):
    def get(self, request):
        form = LoanForm()
        return render(request, 'bank_app/create_loan.html', {'form': form})

    def post(self, request):
        form = LoanForm(request.POST)
        if form.is_valid():
            print(form.errors)
            customer = request.user.customer
            if customer.rank in ['silver', 'gold']:
                loan = form.save(commit=True)
                loan.customer = customer
                loan.save()
                return redirect('bank_app:loan_list')
            else:
                messages.error(request, 'Only customers with silver and gold rank can create loans.')
        return render(request, 'bank_app/create_loan.html', {'form': form})

class MakePaymentView(LoginRequiredMixin, FormView):
    login_url = 'login'
    form_class = PaymentForm
    template_name = 'bank_app/make_payment.html'
    success_url = '/loans/'  # Update with the appropriate URL

    def form_valid(self, form):
        loan_id = self.kwargs['pk']
        payment_amount = form.cleaned_data['payment_amount']

        # Get the loan object
        loan = Loan.objects.get(pk=loan_id)

        # Update the loan balance
        loan.balance -= payment_amount
        loan.save()

        # Create a payment record
        payment = Payment.objects.create(loan=loan, amount=payment_amount)

        # Update loan payment records
        loan.payments.add(payment)

        return super().form_valid(form)

class LoanDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Loan
    template_name = 'bank_app/loan_details.html'
    context_object_name = 'loan'
    
class LogoutView(LogoutView):
    template_name = 'registration/logout.html'
    next_page = reverse_lazy('bank_app:home')

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('bank_app:home')
    
    
class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('bank_app:home')
    
# views.py
class LoanListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Loan
    template_name = 'bank_app/loan_list.html'
    context_object_name = 'loans'

class AccountDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Account
    template_name = 'bank_app/account_details.html'
    context_object_name = 'account'

class LoanListAPIView(APIView):
    def get(self, request):
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### API Views
class ListAccountsAPIView(ListAPIView):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    
class CreateAccountAPIView(CreateAPIView):
    serializer_class = AccountSerializer
    
class RetrieveAccountAPIView(RetrieveAPIView):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    
class UpdateAccountAPIView(UpdateAPIView):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

class DeleteAccountAPIView(DestroyAPIView):
    queryset = Account.objects.all()