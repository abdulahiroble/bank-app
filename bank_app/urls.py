from django.urls import path
from . import views

app_name = 'bank_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('loans/', views.LoanListView.as_view(), name='loan_list'),
    
    # path('accounts/<str:account_number>/', views.AccountDetailsView.as_view(), name='account_details'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/create/', views.CreateAccountView.as_view(), name='create_account'),

    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    # path('customers/<pk>/', views.CustomerDetailView.as_view(), name='customer_details'),
    path('customers/create/', views.CreateCustomerView.as_view(), name='create_customer'),
    path('loans/create/', views.CreateLoanView.as_view(), name='create_loan'),
    path('customers/<int:pk>/change-rank/', views.ChangeCustomerRankView.as_view(), name='change_customer_rank'),
    
]
