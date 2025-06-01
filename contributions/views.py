from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, Contribution, Payout, Notification
from .forms import GroupTypeForm, ContributionGroupForm, MerryGoRoundGroupForm, ContributionForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def dashboard(request):
    groups = request.user.group_memberships.all()
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]  # Last 5 notifications

    # Generate notifications for merry-go-round groups
    for group in groups:
        if group.group_type == 'merry_go_round' and group.amount and group.contribution_period and group.payout_cycle:
            last_payout = group.last_payout_date or timezone.now()
            cycle_days = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30,
            }
            days = cycle_days.get(group.payout_cycle.lower(), 7)
            next_payout_date = last_payout + timedelta(days=days)
            contribution_due_date = next_payout_date - timedelta(days=1)  # 1 day before payout

            if timezone.now().date() >= contribution_due_date.date():
                # Notify all members to contribute
                for member in group.members.all():
                    if not Notification.objects.filter(user=member, group=group, message__contains="Contribute").exists():
                        Notification.objects.create(
                            user=member,
                            group=group,
                            message=f"Reminder: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                            is_admin=False
                        )
                # Notify admin to contribute
                if not Notification.objects.filter(user=group.admin, group=group, message__contains="Admin: Contribute").exists():
                    Notification.objects.create(
                        user=group.admin,
                        group=group,
                        message=f"Admin: Contribute {group.amount} KSH to {group.name} by {next_payout_date.strftime('%Y-%m-%d')}.",
                        is_admin=True
                    )
                # Notify admin to initiate payout if cycle is due
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

    context = {
        'groups': groups,
        'notifications': notifications,
        'user': request.user,
    }
    return render(request, 'contributions/dashboard.html', context)

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
    
    last_payout = group.payouts.order_by('-date').first() if group.group_type == 'merry_go_round' else None
    contributions = Contribution.objects.filter(group=group).order_by('-date')
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

@login_required
def initiate_mpesa_payment(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all() and request.user != group.admin:
        messages.error(request, "You do not have permission to contribute to this group.")
        return redirect('group_detail', group_id=group_id)

    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        phone_number = request.POST.get('phone_number', '')
        if not re.match(r'^\+254[17]\d{8}$', phone_number):
            messages.error(request, "Invalid phone number format. Use +2547XXXXXXXX or +2541XXXXXXXX.")
            return redirect('group_detail', group_id=group_id)

        from .mpesa.stk_push import initiate_stk_push
        response = initiate_stk_push(amount, phone_number, group.phone_number, group.id)
        if response.get('ResponseCode') == '0':
            Contribution.objects.create(
                group=group, user=request.user, amount=amount, phone_number=phone_number, status='Pending'
            )
            messages.success(request, "Payment request sent. Please authorize on your phone.")
        else:
            messages.error(request, f"Failed to initiate payment: {response.get('errorMessage', 'Unknown error')}")
        return redirect('group_detail', group_id=group_id)
    return redirect('group_detail', group_id=group_id)

@csrf_exempt  # M-Pesa callbacks don’t include CSRF tokens
def mpesa_callback(request):
    from .mpesa.callbacks import process_callback
    if request.method == 'POST':
        process_callback(request.body)
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})