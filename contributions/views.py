# contributions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group
from .forms import GroupTypeForm, ContributionGroupForm, MerryGoRoundGroupForm
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    groups = request.user.group_memberships.all()  # Changed from groups to group_memberships
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
        
        return redirect('group_detail', group_id=group.id)

    return render(request, 'contributions/group_detail.html', {'group': group})

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

def help_page(request):
    return render(request, 'contributions/help.html')