# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
import uuid
from django.utils import timezone

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)
    weekly_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    join_code = models.CharField(max_length=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cycle_length = models.PositiveIntegerField(default=7)

    def next_payout(self):
        members = list(self.members.all().order_by('username'))
        last_payout = PayoutCycle.objects.filter(group=self).order_by('-payout_date').first()

        if last_payout:
            last_recipient = last_payout.recipient
            last_index = members.index(last_recipient)
            next_index = (last_index + 1) % len(members)
        else:
            next_index = 0

        next_recipient = members[next_index]
        next_date = self.get_next_payout_date()
        return next_recipient, next_date

    def get_next_payout_date(self):
        today = datetime.now()
        last_payout = PayoutCycle.objects.filter(group=self).order_by('-payout_date').first()
        if last_payout:
            last_date = last_payout.payout_date
        else:
            last_date = today
        next_date = last_date + timedelta(days=self.cycle_length)
        return next_date.replace(hour=8, minute=0, second=0, microsecond=0)

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def add_member(self, user):
        self.members.add(user)

    def remove_member(self, user):
        self.members.remove(user)

    def __str__(self):
        return self.name

class PayoutCycle(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    payout_date = models.DateField(default=date.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient} - {self.payout_date}"

class Contribution(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_date = models.DateField(default=date.today)

    class Meta:
        indexes = [
            models.Index(fields=['group', 'contribution_date']),
        ]

    def __str__(self):
        return f"{self.member} - {self.amount} on {self.contribution_date}"