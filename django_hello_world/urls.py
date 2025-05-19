"""django_hello_world URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contact/', include('contact.urls')),  # Include contact URLs under /contact/
    path('blog/', include('blog.urls')),
    path('store/', include('store.urls')),
    path('events/', include('events.urls')),
    path('users/', include('users.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
] 