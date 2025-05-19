from django.contrib import admin
from .models import EventCategory, Event, Registration

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 1
    raw_id_fields = ('attendee',)
    readonly_fields = ('registration_date',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'venue', 'capacity', 'status', 'available_seats')
    list_filter = ('status', 'category', 'start_date')
    search_fields = ('title', 'description', 'venue', 'address')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('organizer',)
    date_hierarchy = 'start_date'
    ordering = ('start_date',)
    inlines = [RegistrationInline]

    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Available Seats'

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'attendee', 'status', 'registration_date', 'payment_status')
    list_filter = ('status', 'payment_status', 'registration_date')
    search_fields = ('event__title', 'attendee__username', 'notes')
    raw_id_fields = ('event', 'attendee')
    date_hierarchy = 'registration_date'
    ordering = ('-registration_date',)
    actions = ['confirm_registrations', 'mark_as_paid']

    def confirm_registrations(self, request, queryset):
        queryset.update(status='confirmed')
    confirm_registrations.short_description = "Confirm selected registrations"

    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status=True)
    mark_as_paid.short_description = "Mark selected registrations as paid"
