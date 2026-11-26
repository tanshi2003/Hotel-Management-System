"""Central booking lifecycle policy and transition helpers."""
from django.core.exceptions import ValidationError

RECEPTION_TRANSITIONS = {
    'requested': {'pending', 'confirmed', 'canceled'},
    'pending': {'confirmed', 'canceled'},
    'confirmed': {'checked-in', 'canceled'},
    'checked-in': {'checked-out'},
}
PRIVILEGED_TRANSITIONS = {
    **RECEPTION_TRANSITIONS,
    'requested': {'pending', 'confirmed', 'canceled', 'abandoned'},
    'pending': {'confirmed', 'canceled', 'abandoned'},
    'confirmed': {'checked-in', 'canceled', 'abandoned'},
}
GUEST_TRANSITIONS = {
    'requested': {'canceled'},
    'pending': {'canceled'},
    'confirmed': {'canceled'},
}

def transitions_for_role(role):
    if role in ('admin', 'manager'):
        return PRIVILEGED_TRANSITIONS
    if role == 'receptionist':
        return RECEPTION_TRANSITIONS
    if role == 'guest':
        return GUEST_TRANSITIONS
    return {}

def allowed_targets(current, role):
    return transitions_for_role(role).get(current, set())

def can_transition(current, target, role):
    return target in allowed_targets(current, role)

def transition_booking(booking, target, role):
    if not isinstance(target, str) or not can_transition(booking.booking_status, target, role):
        raise ValidationError('Invalid booking status transition: %(current)s -> %(target)s.', params={'current': booking.booking_status, 'target': target})
    booking.booking_status = target
    booking.save(update_fields=['booking_status'])
    return booking
