from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventCategory, Registration
from .forms import EventForm, RegistrationForm

def event_list(request):
    # Get current time
    now = timezone.now()
    print("\n=== Event Filtering Debug ===")
    print(f"Current time: {now}")

    # Get all events for debugging
    all_events = Event.objects.filter(status='published')
    print("\nAll Events:")
    for event in all_events:
        print(f"- {event.title}")
        print(f"  Start: {event.start_date}")
        print(f"  End: {event.end_date}")
        print(f"  Is ongoing: {event.start_date <= now and event.end_date > now}")
        print(f"  Is upcoming: {event.start_date > now}")
        print(f"  Is past: {event.end_date <= now}")
    
    # Get upcoming events (events that haven't started yet)
    upcoming_events = Event.objects.filter(
        status='published',
        start_date__gt=now  # Events that haven't started yet
    ).order_by('start_date')
    
    print(f"\nUpcoming Events ({upcoming_events.count()}):")
    for event in upcoming_events:
        print(f"- {event.title} (Starts: {event.start_date})")
    
    # Get ongoing events (current time is between start and end date)
    ongoing_events = Event.objects.filter(
        status='published',
        start_date__lte=now,  # Started already
        end_date__gt=now      # Not ended yet
    ).order_by('end_date')
    
    print(f"\nOngoing Events ({ongoing_events.count()}):")
    for event in ongoing_events:
        print(f"- {event.title}")
        print(f"  Started: {event.start_date}")
        print(f"  Ends: {event.end_date}")
    
    # Get past events (events that have ended)
    past_events = Event.objects.filter(
        status='published',
        end_date__lte=now     # Already ended
    ).order_by('-end_date')[:5]  # Limit to 5 most recent past events
    
    print(f"\nPast Events ({past_events.count()}):")
    for event in past_events:
        print(f"- {event.title} (Ended: {event.end_date})")
    
    print("\n=== End Debug ===\n")
    
    categories = EventCategory.objects.all()
    
    context = {
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'past_events': past_events,
        'categories': categories,
        'now': now,
    }
    
    return render(request, 'events/event_list.html', context)

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    user_registered = False
    if request.user.is_authenticated:
        user_registered = Registration.objects.filter(event=event, attendee=request.user).exists()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_registered': user_registered
    })

def category_events(request, slug):
    category = get_object_or_404(EventCategory, slug=slug)
    events = Event.objects.filter(
        category=category,
        status='published',
        end_date__gte=timezone.now()
    ).order_by('start_date')
    return render(request, 'events/category_events.html', {
        'category': category,
        'events': events
    })

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_detail', slug=event.slug)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Create New Event'
    })

@login_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.user != event.organizer and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('events:event_detail', slug=event.slug)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Edit Event',
        'event': event
    })

@login_required
def event_delete(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.user != event.organizer and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('events:event_detail', slug=event.slug)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
def event_register(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if event.is_full:
        messages.error(request, 'Sorry, this event is full.')
        return redirect('events:event_detail', slug=event.slug)
    
    if Registration.objects.filter(event=event, attendee=request.user).exists():
        messages.info(request, 'You are already registered for this event.')
        return redirect('events:event_detail', slug=event.slug)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.attendee = request.user
            registration.save()
            messages.success(request, 'You have successfully registered for this event!')
            return redirect('events:event_detail', slug=event.slug)
    else:
        form = RegistrationForm()
    
    return render(request, 'events/registration_form.html', {
        'form': form,
        'event': event
    })

@login_required
def registration_list(request):
    # Get user's registrations ordered by date
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

    return render(request, 'events/registration_list.html', {
        'registrations': registrations,
        'upcoming_events': upcoming_events
    })
