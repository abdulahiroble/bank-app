from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(max_length=50, choices=[('gold', 'Gold'), ('silver', 'Silver'), ('bronze', 'Bronze')])

    def __str__(self):
        return self.user.username

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('C', 'Checking'),
        ('S', 'Savings'),
    )

    IBAN = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.IBAN

    
class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in months")
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, help_text="In percentage %")
    start_date = models.DateField(default=timezone.now, null=True)
    term_in_years = models.PositiveIntegerField(help_text="Loan term in years")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.customer}'s loan ({self.amount}$)"


    def __str__(self):
        return f"{self.customer}'s loan ({self.amount}$)"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('D', 'Deposit'),
        ('W', 'Withdrawal'),
        ('T', 'Transfer'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.date} for {self.account}"

class Payment(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.pk} - Loan: {self.loan}, Amount: {self.amount}"
    

class Transfer(models.Model):
    sender_account = models.ForeignKey(Account, related_name='outgoing_transfers', on_delete=models.CASCADE)
    receiver_account = models.ForeignKey(Account, related_name='incoming_transfers', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)