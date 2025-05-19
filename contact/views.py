from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Inquiry

# Create your views here.

@require_POST
@ensure_csrf_cookie
def submit_inquiry(request):
    try:
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if not email or not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Email and message are required'
            }, status=400)
            
        inquiry = Inquiry.objects.create(
            email=email,
            message=message
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you! Your inquiry has been submitted successfully.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
