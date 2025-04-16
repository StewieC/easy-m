# contributions/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Group(models.Model):
    GROUP_TYPES = (
        ('merry_go_round', 'Merry-Go-Round'),
        ('contribution', 'Contribution'),
    )
    
    name = models.CharField(max_length=100)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES, default='merry_go_round')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')  # Changed related_name
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    join_code = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    
    # Merry-Go-Round specific fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contribution_period = models.CharField(max_length=20, null=True, blank=True)
    payout_cycle = models.CharField(max_length=20, null=True, blank=True)
    savings_enabled = models.BooleanField(default=False)
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)

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