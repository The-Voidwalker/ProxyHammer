"""ProxyHammer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from datetime import datetime
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from hammer import views, forms

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='hammer/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('tools/', views.tools, name='tools'),
    path('execute/<str:tool>', views.execute, name='execute'),
    path('list/', views.list, name='list'),
    path('list/<str:filter>', views.list, name='listf'),
    path('banip/<int:ip_id>', views.banip, name='banip'),
    path('banasn/<int:asn>', views.banasn, name='banasn'),
    path('admin/', admin.site.urls),
]
