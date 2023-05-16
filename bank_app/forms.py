from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Account, Customer, Loan


# class CustomerForm(ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['first_name', 'last_name', 'email', 'rank']
#         widgets = {
#             'rank': forms.RadioSelect
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         email = cleaned_data.get('email')
#         customer_id = self.instance.id if self.instance else None

#         if Customer.objects.filter(email=email).exclude(id=customer_id).exists():
#             raise ValidationError(_('A customer with this email already exists.'))

#         return cleaned_data

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['rank']
        widgets = {
            'rank': forms.RadioSelect
        }

    def clean(self):
        cleaned_data = super().clean()
        # email = cleaned_data.get('email')
        # customer_id = self.instance.id if self.instance else None

        # if Customer.objects.filter(email=email).exclude(id=customer_id).exists():
        #     raise ValidationError(_('A customer with this email already exists.'))

        return cleaned_data

class AccountForm(ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all())

    class Meta:
        model = Account
        fields = ['account_type', 'balance']

    def clean_balance(self):
        balance = self.cleaned_data.get('balance')
        if balance < 0:
            raise ValidationError(_('Balance cannot be negative.'))
        return balance
    


# class AccountForm(ModelForm):
#     class Meta:
#         model = Account
#         fields = ['customer', 'account_type', 'balance']

#     def clean_balance(self):
#         balance = self.cleaned_data.get('balance')
#         if balance < 0:
#             raise ValidationError(_('Balance cannot be negative.'))
#         return balance


class LoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = ['customer', 'amount', 'interest_rate', 'term_in_years']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise ValidationError(_('Amount cannot be negative.'))
        return amount

    def clean_interest_rate(self):
        interest_rate = self.cleaned_data.get('interest_rate')
        if interest_rate < 0:
            raise ValidationError(_('Interest rate cannot be negative.'))
        return interest_rate

    def clean_term_in_years(self):
        term_in_years = self.cleaned_data.get('term_in_years')
        if term_in_years < 0:
            raise ValidationError(_('Term cannot be negative.'))
        return term_in_years

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        if customer and customer.rank == Customer.REGULAR and Loan.objects.filter(customer=customer).exists():
            raise ValidationError(_('A regular customer cannot have more than one active loan.'))
        return cleaned_data
