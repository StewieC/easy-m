# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, PayoutCycle, Contribution
from .forms import GroupForm, ContributionForm, MemberManagementForm
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    next_payouts = PayoutCycle.objects.filter(group__in=groups, status=False).order_by('payout_date')
    return render(request, 'contributions/dashboard.html', {
        'groups': groups,
        'next_payouts': next_payouts,
    })

@login_required
def contribute(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = request.user
            contribution.group = group
            contribution.contribution_date = now().date()
            contribution.save()
            messages.success(request, f"You contributed KES {contribution.amount} to {group.name}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid contribution amount.")
            return render(request, 'contributions/contribute.html', {'form': form})
    form = ContributionForm()
    return render(request, 'contributions/contribute.html', {'form': form})

@login_required
def manage_cycle(request):
    user_groups = Group.objects.filter(members=request.user)
    next_payout = PayoutCycle.objects.filter(group__in=user_groups, status=False).first()

    if next_payout and next_payout.recipient == request.user:
        total_balance = Contribution.objects.filter(group=next_payout.group).aggregate(total=Sum('amount'))['total'] or 0
        interest = total_balance * (next_payout.group.interest_rate / 100)
        payout_amount = total_balance - interest

        next_payout.status = True
        next_payout.save()

        # Schedule next payout cycle
        members = list(next_payout.group.members.all().order_by('username'))
        current_index = members.index(next_payout.recipient)
        next_index = (current_index + 1) % len(members)
        next_recipient = members[next_index]
        next_date = next_payout.group.get_next_payout_date()

        PayoutCycle.objects.create(
            group=next_payout.group,
            recipient=next_recipient,
            payout_date=next_date,
            status=False
        )

        messages.success(request, f"Payout of KES {payout_amount} completed. Next cycle started.")
    else:
        messages.error(request, "No payout available or you are not the recipient.")

    return redirect('dashboard')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group.")
        return redirect('dashboard')

    contributions = group.contribution_set.all()
    total_balance = contributions.aggregate(total=Sum('amount'))['total'] or 0

    form = MemberManagementForm()

    if request.method == 'POST':
        form = MemberManagementForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            action = form.cleaned_data['action']
            if action == 'add':
                group.members.add(user)
                messages.success(request, f"{user.username} added to the group.")
            elif action == 'remove':
                if user == group.admin:
                    messages.error(request, "Admin cannot be removed from the group.")
                else:
                    group.members.remove(user)
                    messages.success(request, f"{user.username} removed from the group.")
            return redirect('group_detail', group_id=group.id)

    next_payout = group.payoutcycle_set.filter(status=False).order_by('payout_date').first()
    if next_payout:
        next_member = next_payout.recipient
        next_payout_date = next_payout.payout_date
    else:
        next_member, next_payout_date = group.next_payout()

    return render(request, 'contributions/group_detail.html', {
        'group': group,
        'form': form,
        'contributions': contributions,
        'total_balance': total_balance,
        'next_member': next_member,
        'next_payout_date': next_payout_date,
        'created_at': group.created_at,
    })

@login_required
def join_group(request):
    if request.method == 'POST':
        join_code = request.POST.get('group_code')
        try:
            group = Group.objects.get(join_code=join_code)
            if request.user in group.members.all():
                messages.info(request, "You are already a member of this group.")
            else:
                group.members.add(request.user)
                messages.success(request, f"You have successfully joined {group.name}.")
        except Group.DoesNotExist:
            messages.error(request, "Invalid join code. Please try again.")
        return redirect('dashboard')
    return render(request, 'contributions/join_group.html')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)

            # Schedule initial payout cycles
            members = list(group.members.all().order_by('username'))
            for i, member in enumerate(members):
                PayoutCycle.objects.create(
                    group=group,
                    recipient=member,
                    payout_date=group.get_next_payout_date() + timedelta(days=group.cycle_length * i),
                    status=False
                )

            messages.success(request, 'Group created successfully!')
            return redirect('dashboard')
    else:
        form = GroupForm()
    return render(request, 'contributions/create_group.html', {'form': form})

@login_required
def contribution_history(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group's history.")
        return redirect('dashboard')

    contributions = group.contribution_set.all().order_by('-contribution_date')
    return render(request, 'contributions/history.html', {
        'group': group,
        'contributions': contributions,
    })

@login_required
def help_page(request):
    return render(request, 'contributions/help.html')