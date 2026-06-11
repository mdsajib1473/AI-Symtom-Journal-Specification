"""Views for the history app: the timeline of past symptom checks."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.checker.models import SymptomCheck


@login_required
def history_list_view(request):
    """Show the logged-in user's non-deleted checks, newest first."""
    checks = SymptomCheck.objects.filter(user=request.user, is_deleted=False)
    return render(request, "history/history_list.html", {"checks": checks})


@login_required
@require_POST
def delete_check_view(request, pk):
    """Soft-delete one of the user's checks and return to the timeline.

    Records are flagged with `is_deleted` rather than removed, so a delete
    can never destroy data. Attempts to delete another user's record get 403.
    """
    check = get_object_or_404(SymptomCheck, pk=pk)
    if check.user_id != request.user.id:
        return HttpResponseForbidden("You cannot delete someone else's entry.")

    check.is_deleted = True
    check.save(update_fields=["is_deleted"])
    messages.success(request, "Entry deleted successfully.")
    return redirect("history:history_list")
