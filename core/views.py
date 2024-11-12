import json

from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import Room, Reservation
from .forms import ReservationForm

class HomeView(ListView):
    model = Room
    template_name = 'core/home.html'

@method_decorator(settings.AUTH.login_required, name='dispatch')
class RoomView(DetailView, FormMixin):
    model = Room
    template_name = 'core/room.html'
    form_class = ReservationForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_data = self.request.session.get('_logged_in_user', {})
        context['user_oid'] = user_data.get('oid')

        context['room_list'] = Room.objects.all().select_related().order_by('floor', 'name')

        room_pk = self.kwargs.get('pk')
        reservation_qs = Reservation.objects.filter(room_id=room_pk)
        events = []
        for reservation in reservation_qs:

            event = {
                'title': reservation.title,
                'start': reservation.start_time.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%dT%H:%M:%S'),
                'end': reservation.end_time.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%dT%H:%M:%S'),
                'backgroundColor': '#8b8b8b',
                'borderColor': '#8b8b8b',
            }
            events.append(event)
        context['events'] = json.dumps(events)

        return context

    def post(self, *args, **kwargs):
        form = ReservationForm(self.request.POST)
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        room_pk = self.kwargs.get('pk')
        return reverse_lazy('room', args=(room_pk,))
