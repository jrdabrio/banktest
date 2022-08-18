from django.test import TestCase
from django.urls import reverse

from ..models import Account, Customer, Transaction


class AccountModelTests(TestCase):
    fixtures = ["customers"]

    def setUp(self):
        """Account test data"""
        first_account, created = Account.objects.get_or_create(
            identifier="ES12 1111 11111", owner=Customer.objects.first()
        )
        second_account, created = Account.objects.get_or_create(
            identifier="ES12 3456 78910", owner=Customer.objects.first()
        )
        Transaction.objects.get_or_create(
            amount=5000, concept="Initial amount", receiver=first_account
        )
        Transaction.objects.get_or_create(amount=3000, receiver=second_account)
        Transaction.objects.get_or_create(
            amount=250,
            origin=first_account,
            receiver=second_account,
            concept="Saturday dinner",
        )
        Transaction.objects.get_or_create(
            amount=700, receiver=first_account, concept="Big present"
        )

    def test_current_amount(self):
        """Check the correcto sum of incomes and payments"""
        self.assertEquals(Account.objects.get(pk=1).current_amount, 5450.0)
        self.assertEquals(Account.objects.get(pk=2).current_amount, 3250.0)

    def test_total_incomes(self):
        """Check the correcto sum of incomes amounts"""
        self.assertEquals(Account.objects.get(pk=1).total_incomes, 5700.0)
        self.assertEquals(Account.objects.get(pk=2).total_incomes, 3250.0)

    def test_total_payments(self):
        """Check the correcto sum of payments amounts"""
        self.assertEquals(Account.objects.get(pk=1).total_payments, 250.0)
        self.assertEquals(Account.objects.get(pk=2).total_payments, 0)
