from django.urls import path
from . import views

app_name = 'bank_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.test, name='register'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('accounts/<str:account_number>/', views.AccountDetailsView.as_view(), name='account_details'),
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('customers/create/', views.CreateCustomerView.as_view(), name='create_customer'),
    path('accounts/create/', views.CreateAccountView.as_view(), name='create_account'),
    path('customers/<int:pk>/change-rank/', views.ChangeCustomerRankView.as_view(), name='change_customer_rank'),
]
