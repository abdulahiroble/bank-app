from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bank_app.urls')),
    path('api/', include_docs_urls(title='APIs')),
    path('api/accounts/', include('bank_app.urls')),  # Assuming you have account-related APIs in 'bank_app.urls'
    path('api/loans/', include('bank_app.urls')),  
]
