from django.db import models

def calculate_family_contribution(family):

    members = family.members.all()
    total_contribution = 0

    for member in members:
        wallet_logs = member.user.wallet_logs.all()
        credit_sum = wallet_logs.filter(action='credit').aggregate(total=models.Sum('coins_amount'))['total'] or 0
        debit_sum = wallet_logs.filter(action='debit').aggregate(total=models.Sum('coins_amount'))['total'] or 0
        total_contribution += (credit_sum - debit_sum)  # নেট অবদান

    return total_contribution
