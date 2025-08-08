"""
Celery tasks for the thermostats application.

These tasks are responsible for scheduling and executing temperature and mode
adjustments around calendar events.  When a booking is about to start, we
pre‑condition the property by setting the HVAC system to an occupied
temperature.  After checkout, we switch to an eco/off setting.

Periodic scanning (via Celery beat) looks ahead to upcoming events and
schedules the appropriate actions using `apply_async` with an ETA.
"""

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from zoneinfo import ZoneInfo

from .models import CalendarEvent
from .thermostat_adapters import get_thermostat_adapter


@shared_task
def pre_arrival_action(event_id: int) -> None:
    """
    Pre‑arrival action: prepare the property for an upcoming booking.

    This task sets the thermostat to occupied mode and a comfortable
    temperature ahead of the guest's arrival.

    Args:
        event_id (int): The ID of the CalendarEvent instance.
    """
    try:
        event = CalendarEvent.objects.select_related('property').get(id=event_id)
    except CalendarEvent.DoesNotExist:
        # Event was deleted before the task ran; nothing to do.
        return

    prop = event.property
    thermostat = prop.thermostats.first()
    if not thermostat:
        # No thermostat associated with this property.
        return

    adapter = get_thermostat_adapter(thermostat)

    # Choose the occupied temperature.  For now we always cool to the default.
    # In the future this could inspect the season or per‑property preferences.
    target_temp = settings.DEFAULT_COOL_TEMP
    try:
        # Turn on the system (cooling mode) and set the target temperature.
        adapter.set_mode('cool')
        adapter.set_temperature(target_temp)
    except Exception as exc:
        # Log the error; Celery will not retry by default.  In a real system you
        # might raise to trigger retry logic or record a failed command.
        raise exc


@shared_task
def post_checkout_action(event_id: int) -> None:
    """
    Post‑checkout action: restore the property to an eco setting after a booking.

    This task is executed a number of hours after the guest checks out.  It
    turns off the HVAC system (or sets it to eco/off) and uses an energy‑saving
    temperature.

    Args:
        event_id (int): The ID of the CalendarEvent instance.
    """
    try:
        event = CalendarEvent.objects.select_related('property').get(id=event_id)
    except CalendarEvent.DoesNotExist:
        return

    prop = event.property
    thermostat = prop.thermostats.first()
    if not thermostat:
        return

    adapter = get_thermostat_adapter(thermostat)

    # Use eco temperatures; for simplicity we'll apply the cooling eco value.
    eco_temp = settings.DEFAULT_ECO_COOL_TEMP
    try:
        adapter.set_mode('off')
        adapter.set_temperature(eco_temp)
    except Exception as exc:
        raise exc


@shared_task
def scan_calendar_events() -> None:
    """
    Scan upcoming calendar events and schedule pre/post actions.

    This task runs periodically (configured via Celery beat) and inspects
    CalendarEvent instances.  For each event, it calculates when the pre‑arrival
    and post‑checkout tasks should run based on the property's timezone and
    global offsets.  It then schedules the tasks using apply_async with an ETA.
    """
    now = timezone.now()
    upcoming_events = CalendarEvent.objects.select_related('property').filter(
        end_date__gte=now
    )

    for event in upcoming_events:
        prop = event.property
        tzname = getattr(prop, 'timezone', None) or settings.DEFAULT_PROPERTY_TIME_ZONE
        try:
            tz = ZoneInfo(tzname)
        except Exception:
            # Fall back to the Django default timezone if invalid.
            tz = ZoneInfo(settings.TIME_ZONE)

        # Convert start/end to the property's local timezone.
        start_local = event.start_date
        end_local = event.end_date
        if timezone.is_aware(start_local):
            start_local = start_local.astimezone(tz)
        else:
            start_local = timezone.make_aware(start_local, timezone=tz)

        if timezone.is_aware(end_local):
            end_local = end_local.astimezone(tz)
        else:
            end_local = timezone.make_aware(end_local, timezone=tz)

        pre_time = start_local - timedelta(hours=settings.PRE_ARRIVAL_HOURS)
        post_time = end_local + timedelta(hours=settings.POST_CHECKOUT_HOURS)

        # Only schedule tasks for times in the future.
        if pre_time > now:
            pre_arrival_action.apply_async(args=[event.id], eta=pre_time)

        if post_time > now:
            post_checkout_action.apply_async(args=[event.id], eta=post_time)