# contributions/forms.py
from django import forms
from .models import Group, Contribution

class GroupTypeForm(forms.Form):
    group_type = forms.ChoiceField(choices=Group.GROUP_TYPES, widget=forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}))

class ContributionGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Group Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': '+254712345678'}),
        }

class MerryGoRoundGroupForm(forms.ModelForm):
    CONTRIBUTION_PERIODS = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    PAYOUT_CYCLES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    contribution_period = forms.ChoiceField(choices=CONTRIBUTION_PERIODS, widget=forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}))
    payout_cycle = forms.ChoiceField(choices=PAYOUT_CYCLES, widget=forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}))
    savings_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'mr-2'}))
    savings_amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Savings Amount per Cycle'}))

    class Meta:
        model = Group
        fields = ['name', 'amount', 'phone_number', 'contribution_period', 'payout_cycle', 'savings_enabled', 'savings_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Group Name'}),
            'amount': forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Contribution Amount'}),
            'phone_number': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': '+254712345678'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        savings_enabled = cleaned_data.get('savings_enabled')
        savings_amount = cleaned_data.get('savings_amount')

        if savings_enabled and (savings_amount is None or savings_amount <= 0):
            raise forms.ValidationError("Please provide a valid savings amount when savings is enabled.")
        return cleaned_data

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Amount to Contribute'}),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if self.group and self.group.group_type == 'merry_go_round':
            self.fields['amount'].initial = self.group.amount
            self.fields['amount'].widget.attrs['readonly'] = True