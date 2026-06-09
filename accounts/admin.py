from django.contrib import admin
from .models import UserProfile, Tour, Booking, Document

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'role', 'phone', 'nationality', 'language')
    list_filter   = ('role',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display  = ('name', 'location', 'duration', 'price', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('client', 'tour_name', 'travel_date', 'num_people', 'status', 'total_price')
    list_filter   = ('status', 'travel_date')
    search_fields = ('client__first_name', 'client__last_name', 'tour_name')
    raw_id_fields = ('client',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'booking', 'uploaded_at')
