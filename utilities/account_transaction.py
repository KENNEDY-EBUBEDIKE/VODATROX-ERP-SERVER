from .base_transaction import BaseTransaction
from . import errors
from apps.account.models import Account
from apps.account.models import CreditTransaction as CreditTrans
from apps.account.models import Transaction


class CreditTransaction(BaseTransaction):
    """ Deposit Transaction processor """

    source = None

    def _prepare_transaction(self, *args, **kwargs):
        """Arrange and validate the necessary data for the transaction"""
        self.amount = kwargs['deposit_transaction'].amount
        self.reference = kwargs['deposit_transaction'].reference
        self.source = kwargs['source']

    def set_balances(self, deposit_transaction, account):
        """Set balances and
        Make the method chainable"""
        # @TODO: Implement it

        self.balance_before = account.account_balance
        self.balance_after = deposit_transaction.amount + self.balance_before
        self.new_balance = self.balance_after

        return True, self

    def initiate(self, *args, **kwargs):
        """Finalise the transaction"""

        self._prepare_transaction(
            deposit_transaction=kwargs['deposit_transaction'],
            source=kwargs['source']
        ),

        transaction = Transaction.objects.create(
            initiator=f"{kwargs['deposit_transaction'].deposit.transaction.sales_person.user.first_name} "
                      f"{kwargs['deposit_transaction'].deposit.transaction.sales_person.user.surname}",
            amount=self.amount,
            balance_before=self.balance_before,
            balance_after=self.balance_after,
            transaction_reference=self.reference,
            transaction_type="CREDIT",
            transaction_details=kwargs['deposit_transaction'].deposit.transaction.transaction_details,
            source=self.source,
            transaction_date=kwargs['deposit_transaction'].deposit.transaction.transaction_date,
        )

        crd = CreditTrans.objects.create(
            transaction=transaction,
            account=kwargs['account']
        )

        kwargs['deposit_transaction'].deposit.credit = crd
        kwargs['deposit_transaction'].deposit.save()

        kwargs['account'].account_balance = self.new_balance
        kwargs['account'].save()
        return True, crd


class DebitTransaction(BaseTransaction):
    """ Supply Transaction processor """
    pass
