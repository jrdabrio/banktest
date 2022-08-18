import json

from django.test import TestCase
from django.urls import reverse

from rest_framework.serializers import ValidationError

from ..models import Account, Customer, Transaction


class AccountApiTests(TestCase):
    fixtures = ["customers"]

    def setUp(self):
        """Account test data"""
        first_account, created = Account.objects.get_or_create(
            identifier="ES12 1111 11111", owner=Customer.objects.first()
        )
        second_account, created = Account.objects.get_or_create(
            identifier="ES12 3456 78910", owner=Customer.objects.first()
        )
        Transaction.objects.get_or_create(amount=5000, receiver=first_account)
        Transaction.objects.get_or_create(amount=3000, receiver=second_account)
        Transaction.objects.get_or_create(
            amount=250, origin=first_account, receiver=second_account
        )

    def test_list(self):
        """Check if GET function returns all accounts"""
        response = self.client.get(reverse("bank:account-list"))

        self.assertContains(response, "ES12 1111 11111")
        self.assertContains(response, "ES12 3456 78910")

    def test_detail(self):
        """GET an account and check his related information"""
        response = self.client.get(reverse("bank:account-detail", kwargs={"pk": 1}))
        data = json.loads(response.content)
        content = {
            "id": 1,
            "identifier": "ES12 1111 11111",
            "owner": 1,
            "incomes": [1],
            "payments": [3],
            "current_amount": 4750.0,
        }
        self.assertEquals(data, content)

    def test_create(self):
        """Create an account and his initial transaction"""
        last_customer_id = Customer.objects.last().id
        post = json.dumps(
            {
                "identifier": "ES00 0000 00000",
                "owner": last_customer_id,
                "incomes": [{"concept": "Initial amount", "amount": 2000}],
            }
        )
        response = self.client.post(
            reverse("bank:account-list"), post, content_type="application/json"
        )
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        content = {
            "id": 3,
            "identifier": "ES00 0000 00000",
            "owner": last_customer_id,
            "incomes": [4],
            "payments": [],
            "current_amount": 2000.0,
        }
        self.assertEquals(data, content)
        self.assertEquals(Account.objects.count(), 3)

    def test_create_whitout_income(self):
        """Create an account without initial transaction, expecting a validation error"""
        last_customer_id = Customer.objects.last().id
        post = json.dumps(
            {
                "identifier": "ES00 0000 00000",
                "owner": last_customer_id,
            }
        )
        response = self.client.post(
            reverse("bank:account-list"), post, content_type="application/json"
        )
        self.assertEquals(response.status_code, 400)
        self.assertRaisesMessage(ValidationError, "You must specify an initial amount")


class AccountTransferApiTests(TestCase):
    fixtures = ["customers"]

    def setUp(self):
        """Account test data"""
        first_account, created = Account.objects.get_or_create(
            identifier="ES12 1111 11111", owner=Customer.objects.first()
        )
        second_account, created = Account.objects.get_or_create(
            identifier="ES12 3456 78910", owner=Customer.objects.first()
        )
        Transaction.objects.get_or_create(amount=5000, receiver=first_account)
        Transaction.objects.get_or_create(amount=3000, receiver=second_account)

    def test_correct_transfer(self):
        """Create a transaction from account used as detail"""
        post = json.dumps({"concept": "Piano classes", "amount": 500, "receiver": 2})
        response = self.client.post(
            reverse("bank:account-transfer-amount", kwargs={"pk": 1}),
            post,
            content_type="application/json",
        )
        data = json.loads(response.content)
        data.pop("creation_datetime")
        self.assertEquals(response.status_code, 201)
        content = {
            "id": 3,
            "concept": "Piano classes",
            "origin": 1,
            "receiver": 2,
            "amount": 500.0,
        }
        self.assertEquals(data, content)
        self.assertEquals(Account.objects.get(pk=1).current_amount, 4500.0)
        self.assertEquals(Account.objects.get(pk=2).current_amount, 3500.0)

    def test_exceded_amount_transfer(self):
        """Create a transaction with amount greater than available amount"""
        post = json.dumps({"concept": "Gold carrots", "amount": 500000, "receiver": 2})
        response = self.client.post(
            reverse("bank:account-transfer-amount", kwargs={"pk": 1}),
            post,
            content_type="application/json",
        )
        self.assertEquals(response.status_code, 400)
        self.assertRaisesMessage(
            ValidationError, "Origin balance is less than the amount requested"
        )


class AccountBalanceApiTests(TestCase):
    fixtures = ["customers"]

    def setUp(self):
        """Account test data"""
        first_account, created = Account.objects.get_or_create(
            identifier="ES12 1111 11111", owner=Customer.objects.first()
        )
        second_account, created = Account.objects.get_or_create(
            identifier="ES12 3456 78910", owner=Customer.objects.first()
        )
        Transaction.objects.get_or_create(amount=5000, receiver=first_account)
        Transaction.objects.get_or_create(amount=3000, receiver=second_account)
        Transaction.objects.get_or_create(
            amount=250, origin=first_account, receiver=second_account
        )

    def test_balance(self):
        """GET an account and check his total payments, incomes and current balance"""
        response = self.client.get(reverse("bank:account-balance", kwargs={"pk": 1}))
        data = json.loads(response.content)
        content = {
            "payments": 250,
            "incomes": 5000,
            "current_balance": 4750,
        }
        self.assertEquals(data, content)


class AccountHistoryApiTests(TestCase):
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

    def test_balance(self):
        """GET an account and check all his transactions"""
        response = self.client.get(reverse("bank:account-history", kwargs={"pk": 1}))
        data = json.loads(response.content)

        self.assertContains(response, "Initial amount")
        self.assertContains(response, "Saturday dinner")
        self.assertContains(response, "Big present")
        self.assertEqual(len(data), 3)
