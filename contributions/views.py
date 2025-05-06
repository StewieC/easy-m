# contributions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, Contribution, Payout
from .forms import GroupTypeForm, ContributionGroupForm, MerryGoRoundGroupForm, ContributionForm
from django.contrib.auth.models import User
from datetime import datetime

@login_required
def dashboard(request):
    groups = request.user.group_memberships.all()
    return render(request, 'contributions/dashboard.html', {'groups': groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupTypeForm(request.POST)
        if form.is_valid():
            group_type = form.cleaned_data['group_type']
            request.session['group_type'] = group_type
            if group_type == 'contribution':
                return redirect('create_contribution_group')
            else:
                return redirect('create_merry_go_round_group')
    else:
        form = GroupTypeForm()
    return render(request, 'contributions/create_group.html', {'form': form})

@login_required
def create_contribution_group(request):
    if request.method == 'POST':
        form = ContributionGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.group_type = 'contribution'
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = ContributionGroupForm()
    return render(request, 'contributions/create_contribution_group.html', {'form': form})

@login_required
def create_merry_go_round_group(request):
    if request.method == 'POST':
        form = MerryGoRoundGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.group_type = 'merry_go_round'
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = MerryGoRoundGroupForm()
    return render(request, 'contributions/create_merry_go_round_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all() and request.user != group.admin:
        messages.error(request, "You do not have permission to view this group.")
        return redirect('dashboard')
    
    # Get the last payout for Merry-Go-Round groups
    last_payout = group.payouts.order_by('-date').first() if group.group_type == 'merry_go_round' else None
    
    # Get contribution history for the group
    contributions = Contribution.objects.filter(group=group).order_by('-date')
    
    # Get next payout for Merry-Go-Round groups
    next_payout = None
    if group.group_type == 'merry_go_round':
        next_payout = group.get_next_payout()

    if request.method == 'POST':
        if 'add_user' in request.POST:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                if user not in group.members.all():
                    group.members.add(user)
                    messages.success(request, f"Added {user.username} to the group.")
                else:
                    messages.warning(request, f"{user.username} is already a member of the group.")
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
        
        elif 'remove_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user != group.admin:
                group.members.remove(user)
                messages.success(request, f"Removed {user.username} from the group.")
            else:
                messages.error(request, "Cannot remove the group admin.")
        
        elif 'make_payout' in request.POST and group.group_type == 'merry_go_round':
            if request.user == group.admin:
                next_payout_data = group.get_next_payout()
                if next_payout_data:
                    Payout.objects.create(
                        group=group,
                        recipient=next_payout_data['recipient'],
                        amount=next_payout_data['amount']
                    )
                    group.last_payout_date = datetime.now()
                    group.save()
                    messages.success(request, f"Payout of {next_payout_data['amount']} KSH made to {next_payout_data['recipient'].username}.")
                else:
                    messages.error(request, "No members available for payout.")
            else:
                messages.error(request, "Only the admin can make payouts.")
        
        elif 'contribute' in request.POST:
            form = ContributionForm(request.POST, group=group)
            if form.is_valid():
                contribution = form.save(commit=False)
                contribution.group = group
                contribution.user = request.user
                contribution.save()
                messages.success(request, f"Contributed {contribution.amount} KSH to {group.name}.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            return redirect('group_detail', group_id=group.id)

    form = ContributionForm(group=group)
    return render(request, 'contributions/group_detail.html', {
        'group': group,
        'last_payout': last_payout,
        'contributions': contributions,
        'next_payout': next_payout,
        'form': form,
    })

@login_required
def join_group(request):
    if request.method == 'POST':
        join_code = request.POST.get('join_code')
        group = get_object_or_404(Group, join_code=join_code)
        if request.user not in group.members.all():
            group.members.add(request.user)
            messages.success(request, f"You have joined the group '{group.name}'!")
        else:
            messages.warning(request, "You are already a member of this group.")
        return redirect('group_detail', group_id=group.id)
    return render(request, 'contributions/join_group.html')