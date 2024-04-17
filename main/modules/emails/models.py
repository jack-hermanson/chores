from dataclasses import dataclass

from main.modules.accounts.models import Account
from main.modules.chore_logs.models import ChoreLog


@dataclass
class AccountWithChoreLogs:
    chore_logs: list[ChoreLog]
    account: Account
