import json
import random
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
import requests

from django.core.cache import cache

from twilio.rest import Client

from .models import Customer, Account, Loan, Transaction, Payment, Transfer
from .forms import CustomerForm, AccountForm, LoanForm, PaymentForm, SMSVerificationForm, TransferForm

from django.views.generic import TemplateView, ListView

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework import status
from .models import Loan
from .serializers import LoanSerializer, AccountSerializer, TransferSerializer
from bank_app import serializers


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

class CreateCustomerView(View):
    def get(self, request):
        user_form = UserCreationForm()
        customer_form = CustomerForm()
        return render(request, 'bank_app/create_customer.html', {'user_form': user_form, 'customer_form': customer_form})

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()
            return redirect('bank_app:customer_list')
        return render(request, 'bank_app/create_customer.html', {'user_form': user_form, 'customer_form': customer_form})

class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Customer
    form_class = CustomerForm
    template_name = 'bank_app/update_customer.html'
    success_url = reverse_lazy('bank_app:customer_list')


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

class UserAccountListView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        try:
            customer = request.user.customer
            accounts = Account.objects.filter(owner=customer)
        except AttributeError:
            accounts = []
        
        return render(request, 'bank_app/user_account_list.html', {'accounts': accounts})


class CreateAccountView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Account
    form_class = AccountForm
    template_name = 'bank_app/create_account.html'
    success_url = reverse_lazy('bank_app:home')



class CreateLoanView(LoginRequiredMixin, CreateView):
    model = Loan
    form_class = LoanForm
    template_name = 'bank_app/create_loan.html'
    success_url = reverse_lazy('bank_app:home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        customer = self.request.user.customer
        accounts = Account.objects.filter(owner=customer)
        form.fields['account'].queryset = accounts
        return form

    def form_valid(self, form):
        customer = self.request.user.customer
        account = form.cleaned_data['account']
        loan_amount = form.cleaned_data['amount']

        if customer.rank in ['silver', 'gold']:
            # Add the loan amount to the selected account balance
            account.balance += loan_amount
            account.save()

            # Create the loan
            loan = form.save(commit=False)
            loan.customer = customer
            loan.save()

            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Only customers with silver and gold rank can create loans.')
            return self.form_invalid(form)
        

class MakePaymentView(LoginRequiredMixin, FormView):
    login_url = 'login'
    form_class = PaymentForm
    template_name = 'bank_app/make_payment.html'
    success_url = reverse_lazy('bank_app:home')

    def form_valid(self, form):
        loan_id = self.kwargs['pk']
        payment_amount = form.cleaned_data['payment_amount']
        account = form.cleaned_data['account']

        # Get the loan object
        loan = Loan.objects.get(pk=loan_id)

        # Deduct payment amount from account balance
        account.balance -= payment_amount
        account.save()

        # Update the loan balance
        loan.balance += payment_amount
        loan.amount -= payment_amount
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
    
class TransferCreateView(generics.CreateAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

class TransferDetailView(generics.RetrieveAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
        
class CreateTransferView(LoginRequiredMixin, View):
    form_class = TransferForm
    template_name = 'bank_app/create_transfer.html'
    success_url = reverse_lazy('bank_app:create_transfer')
    
    def get(self, request):
        form = self.form_class()
        account = request.user.customer
        accounts = Account.objects.filter(owner=account)
        form.fields['sender_account'].queryset = accounts
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            sender_account = form.cleaned_data['sender_account']
            receiver_account = form.cleaned_data['receiver_account']
            amount = form.cleaned_data['amount']
            
            # Perform additional validation and business logic
            if sender_account.balance >= amount:
                # Sufficient balance, proceed with the transfer
                sender_account.balance -= amount
                receiver_account.balance += amount
                sender_account.save()
                receiver_account.save()
                
                # Create and save the transfer record
                transfer = Transfer(sender_account=sender_account, receiver_account=receiver_account, amount=amount)
                transfer.save()
                
                # Serialize the transfer data
                payload = {
                    'sender_account': sender_account.id,
                    'receiver_account': receiver_account.id,
                    'amount': str(amount),
                }
                json_payload = json.dumps(payload)
                
                # Send the transfer data to the other Django instance
                api_url = 'http://localhost:7000/api/transfers/'
                headers = {'Content-Type': 'application/json'}
                response = requests.post(api_url, data=json_payload, headers=headers)
                
                if response.status_code == 201:
                    # Transfer data sent successfully to the other instance
                    return redirect(self.success_url)
                else:
                    # Error occurred while sending the transfer data
                    form.add_error(None, 'An error occurred while sending the transfer.')
        
        return render(request, self.template_name, {'form': form})


class TransferCreateView(generics.CreateAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

    def perform_create(self, serializer):
        sender_account = serializer.validated_data['sender_account']
        receiver_account = serializer.validated_data['receiver_account']
        amount = serializer.validated_data['amount']

        # if sender_account.balance < amount:
        #     raise serializers.ValidationError("Insufficient funds.")

        # sender_account.balance -= amount
        # sender_account.save()

        # receiver_account.balance += amount
        # receiver_account.save()

        # serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class SMSVerificationView(FormView):
    form_class = SMSVerificationForm
    template_name = 'bank_app/sms_verification.html'
    success_url = '/verify-code/'  # Replace with your desired success URL

    def form_valid(self, form):
        # Get the phone number from the form
        phone_number = form.cleaned_data['phone_number']

        # Generate a random verification code (you can customize this logic)
        verification_code = generate_verification_code()

        # Save the verification code in the session (or you can store it in the database)
        self.request.session['verification_code'] = verification_code

        cache.set(f"verification_code:{phone_number}", verification_code)

        # Send the SMS verification code using Twilio
        send_sms_verification(phone_number, verification_code)

        return super().form_valid(form)

def generate_verification_code():
        verification_code = random.randint(100000, 999999)
        return verification_code

def send_sms_verification(phone_number, verification_code):
    # Replace with your Twilio account SID and auth token
    account_sid = 'AC8c82b8ec978b729894050ad6643a338d'
    auth_token = '13ef0b92865f81892769983b72b302c7'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Replace with your Twilio phone number
    twilio_phone_number = '+19452073127'

    # Compose the SMS message
    message = f"Your verification code is: {verification_code}"

    # Send the SMS message using Twilio
    client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=phone_number
    )

class VerifyCodeView(View):
    def get(self, request):
        return render(request, 'bank_app/verify_code.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        verification_code = request.POST.get('verification_code')

        # Retrieve the stored verification code and message SID from cache
        stored_verification_code = cache.get(f"verification_code:{phone_number}")
        message_sid = cache.get(f"message_sid:{phone_number}")

        if verification_code == stored_verification_code:
          
        

            # Clear the verification code and message SID from cache
            cache.delete(f"verification_code:{phone_number}")
            cache.delete(f"message_sid:{phone_number}")

            return redirect('bank_app:sms_verification')
        else:
            # Verification code does not match
            messages.error(request, 'Invalid verification code.')

        return redirect('bank_app:verify_code')
