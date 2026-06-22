"""Admin registration for the built-in User model (study participant roster)."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Replace the default User admin so we can tune the columns and filters while
# keeping UserAdmin's secure password-change form.
admin.site.unregister(User)


@admin.register(User)
class StudyUserAdmin(UserAdmin):
    """User list tuned for managing study participants."""

    list_display = ("username", "email", "date_joined", "last_login", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_active", "date_joined")
