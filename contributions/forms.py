# forms.py
from django import forms
from .models import Contribution, Group
from django.contrib.auth.models import User

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'weekly_contribution', 'interest_rate', 'cycle_length']
        widgets = {
            'cycle_length': forms.NumberInput(attrs={'min': 1}),
        }
        labels = {
            'cycle_length': 'Cycle Length (in days)',
        }

class MemberManagementForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')], label="Action")