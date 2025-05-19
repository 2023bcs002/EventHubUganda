from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from blog.models import Post, Comment
from events.models import Event, Registration
from django.core.paginator import Paginator
from django.db.models import Count
from .forms import CustomSignupForm

@login_required
def profile(request):
    return render(request, 'users/profile.html', {
        'user': request.user
    })

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('account_login')
    else:
        form = CustomSignupForm()
    
    return render(request, 'account/signup.html', {
        'form': form
    })

@login_required
def user_dashboard(request):
    # Get user's posts
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # Get user's comments
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    # Get comments on user's posts
    comments_on_posts = Comment.objects.filter(
        post__author=request.user
    ).select_related('post', 'author').order_by('-created_at')
    
    # Get post interaction stats
    posts_with_comment_count = Post.objects.filter(
        author=request.user
    ).annotate(comment_count=Count('comments'))
    
    # Get user's registered events
    registrations = Registration.objects.filter(
        attendee=request.user
    ).select_related('event').order_by('-registration_date')

    # Get upcoming events (excluding ones user is already registered for)
    registered_event_ids = registrations.values_list('event_id', flat=True)
    upcoming_events = Event.objects.filter(
        status='published',
        end_date__gte=timezone.now()
    ).exclude(
        id__in=registered_event_ids
    ).order_by('start_date')[:5]  # Show only next 5 upcoming events
    
    # Paginate posts
    paginator = Paginator(user_posts, 5)  # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'comments': user_comments[:5],  # Show last 5 comments
        'comments_on_posts': comments_on_posts[:10],  # Show last 10 comments on user's posts
        'posts_with_comments': posts_with_comment_count,
        'registrations': registrations[:5],  # Show last 5 registered events
        'upcoming_events': upcoming_events,
        'total_posts': user_posts.count(),
        'total_comments': user_comments.count(),
        'total_comments_received': comments_on_posts.count(),
        'total_events': registrations.count(),
    }
    
    return render(request, 'users/dashboard.html', context) 