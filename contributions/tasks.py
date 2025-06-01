from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Group, Notification

@shared_task
def check_group_cycles():
    groups = Group.objects.filter(group_type='merry_go_round')
    for group in groups:
        last_payout = group.last_payout_date or timezone.now()
        cycle_days = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days = cycle_days.get(group.payout_cycle.lower(), 7)
        next_payout_date = last_payout + timedelta(days=days)
        contribution_due_date = next_payout_date - timedelta(days=1)

        if timezone.now().date() >= contribution_due_date.date():
            for member in group.members.all():
                if not Notification.objects.filter(user=member, group=group, message__contains="Contribute").exists():
                    Notification.objects.create(
                        user=member,
                        group=group,
                        message=f"Reminder: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                        is_admin=False
                    )
            if not Notification.objects.filter(user=group.admin, group=group, message__contains="Admin: Contribute").exists():
                Notification.objects.create(
                    user=group.admin,
                    group=group,
                    message=f"Admin: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                    is_admin=True
                )
            if timezone.now().date() >= next_payout_date.date() and not Notification.objects.filter(user=group.admin, group=group, message__contains="Payout").exists():
                next_payout = group.get_next_payout()
                if next_payout:
                    Notification.objects.create(
                        user=group.admin,
                        group=group,
                        message=f"Admin: Payout {next_payout['amount']} KSH to {next_payout['recipient'].username} for {group.name} by {next_payout['date'].strftime('%Y-%m-%d')}.",
                        is_admin=True
                    )
                    group.last_payout_date = timezone.now()
                    group.save()
                    
from .mpesa.b2c import initiate_b2c_payment

# Move payout logic inside the check_group_cycles function, after payout notification
@shared_task
def check_group_cycles():
    groups = Group.objects.filter(group_type='merry_go_round')
    for group in groups:
        last_payout = group.last_payout_date or timezone.now()
        cycle_days = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days = cycle_days.get(group.payout_cycle.lower(), 7)
        next_payout_date = last_payout + timedelta(days=days)
        contribution_due_date = next_payout_date - timedelta(days=1)

        if timezone.now().date() >= contribution_due_date.date():
            for member in group.members.all():
                if not Notification.objects.filter(user=member, group=group, message__contains="Contribute").exists():
                    Notification.objects.create(
                        user=member,
                        group=group,
                        message=f"Reminder: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                        is_admin=False
                    )
            if not Notification.objects.filter(user=group.admin, group=group, message__contains="Admin: Contribute").exists():
                Notification.objects.create(
                    user=group.admin,
                    group=group,
                    message=f"Admin: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                    is_admin=True
                )
            if timezone.now().date() >= next_payout_date.date() and not Notification.objects.filter(user=group.admin, group=group, message__contains="Payout").exists():
                next_payout = group.get_next_payout()
                if next_payout:
                    Notification.objects.create(
                        user=group.admin,
                        group=group,
                        message=f"Admin: Payout {next_payout['amount']} KSH to {next_payout['recipient'].username} for {group.name} by {next_payout['date'].strftime('%Y-%m-%d')}.",
                        is_admin=True
                    )
                    # Initiate B2C payment here
                    response = initiate_b2c_payment(next_payout['amount'], next_payout['recipient'].profile.phone_number, group.phone_number)
                    if response.get('ResponseCode') == '0':
                        from .models import Payout  # Import here to avoid circular import
                        Payout.objects.create(group=group, recipient=next_payout['recipient'], amount=next_payout['amount'])
                        group.last_payout_date = timezone.now()
                        group.save()
                        Notification.objects.create(
                            user=group.admin, group=group, message=f"Payout of {next_payout['amount']} KSH to {next_payout['recipient'].username} completed.",
                            is_admin=True
                        )