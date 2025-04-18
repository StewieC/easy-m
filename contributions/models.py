# contributions/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta

class Group(models.Model):
    GROUP_TYPES = (
        ('merry_go_round', 'Merry-Go-Round'),
        ('contribution', 'Contribution'),
    )
    
    name = models.CharField(max_length=100)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES, default= 'Contributions')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    join_code = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
        
    # Merry-Go-Round specific fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contribution_period = models.CharField(max_length=20, null=True, blank=True)
    payout_cycle = models.CharField(max_length=20, null=True, blank=True)
    savings_enabled = models.BooleanField(default=False)
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    last_payout_date = models.DateTimeField(null=True, blank=True)  # Track the last payout date

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.group_type == 'merry_go_round' and self.amount and self.contribution_period:
            member_count = self.members.count() or 3
            savings_text = f"with each member saving {self.savings_amount} KSH per cycle" if self.savings_enabled else "with full payouts to one member each cycle"
            self.description = (
                f"This is a Merry-Go-Round group where {member_count} members contribute {self.amount} KSH "
                f"{self.contribution_period}. Payouts occur {self.payout_cycle}, {savings_text}."
            )
        super().save(*args, **kwargs)

    def get_next_payout(self):
        if self.group_type != 'merry_go_round':
            return None
        
        # Calculate the next payout date based on the payout cycle
        if not self.last_payout_date:
            # If no payout has happened, assume the first payout is today
            last_date = datetime.now()
        else:
            last_date = self.last_payout_date

        # Map payout cycle to days
        cycle_days = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
        }
        days = cycle_days.get(self.payout_cycle, 7)  # Default to weekly if not specified
        next_date = last_date + timedelta(days=days)

        # Determine the next recipient (rotate through members)
        members = list(self.members.all())
        if not members:
            return None

        last_payout = self.payouts.order_by('-date').first()
        if last_payout:
            last_recipient = last_payout.recipient
            last_index = members.index(last_recipient) if last_recipient in members else -1
            next_index = (last_index + 1) % len(members)
        else:
            next_index = 0

        next_recipient = members[next_index]
        
        # Calculate payout amount
        member_count = len(members)
        if self.savings_enabled:
            payout_amount = (self.amount * member_count) - (self.savings_amount * member_count)
        else:
            payout_amount = self.amount * member_count

        return {
            'recipient': next_recipient,
            'date': next_date,
            'amount': payout_amount,
        }

    def total_contributions(self):
        return sum(contribution.amount for contribution in self.contributions.all())

class Contribution(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} contributed {self.amount} to {self.group.name}"

class Payout(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='payouts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payout of {self.amount} to {self.recipient.username} on {self.date}"