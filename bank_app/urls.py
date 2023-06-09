from django.urls import path
from . import views
from .views import CreateAccountAPIView, LoanListAPIView, RetrieveAccountAPIView, UpdateAccountAPIView, DeleteAccountAPIView, ListAccountsAPIView, UserAccountListView

app_name = 'bank_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('send-verification/', views.SMSVerificationView.as_view(), name='send_verification'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_details'),
    path('accounts/create/', views.CreateAccountView.as_view(), name='create_account'),
    path('user-accounts/', UserAccountListView.as_view(), name='user_account_list'),

    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', views.CreateCustomerView.as_view(), name='create_customer'),
    path('customers/<int:pk>/change-rank/', views.ChangeCustomerRankView.as_view(), name='change_customer_rank'),
    path('customers/update/<int:pk>/', views.UpdateCustomerView.as_view(), name='customer_update'),
    
    path('loans/', views.LoanListView.as_view(), name='loan_list'),
    path('loans/create/', views.CreateLoanView.as_view(), name='create_loan'),
    path('loans/<int:pk>/make-payment/', views.MakePaymentView.as_view(), name='make_payment'),
    path('loans/<int:pk>/', views.LoanDetailView.as_view(), name='loan_details'),
    
    # path('transfers/', views.TransferListView.as_view(), name='transfer_list'),
    path('transfers/create/', views.CreateTransferView.as_view(), name='create_transfer'),
    path('transfers/<int:pk>/', views.TransferDetailView.as_view(), name='transfer_details'),

    path('api/transfers/', views.TransferCreateView.as_view(), name='create_transfer2'),
    path('api/transfers/<int:pk>/', views.TransferDetailView.as_view(), name='transfer_detail'),

    path('api/loans/', LoanListAPIView.as_view(), name='loan-list'),
    
    path('api/accounts/', ListAccountsAPIView.as_view(), name='list-accounts'),
    path('api/accounts/create/', CreateAccountAPIView.as_view(), name='create-account'),
    path('api/accounts/<int:pk>/', RetrieveAccountAPIView.as_view(), name='retrieve-account'),
    path('api/accounts/<int:pk>/update/', UpdateAccountAPIView.as_view(), name='update-account'),
    path('api/accounts/<int:pk>/delete/', DeleteAccountAPIView.as_view(), name='delete-account'),
    
    path('api/token/', views.CustomAuthToken.as_view(), name='api_token'),
]
