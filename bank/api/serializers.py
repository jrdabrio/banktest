from django.utils.translation import ugettext_lazy as _

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from ..models import Account, Customer, Transaction


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name")


class TransactionSerializer(FlexFieldsModelSerializer):
    creation_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False, read_only=True
    )

    class Meta:
        model = Transaction
        fields = ("id", "concept", "amount", "origin", "receiver", "creation_datetime")

    def validate(self, data):
        origin = data.get("origin")
        receiver = data.get("receiver")

        if origin == receiver:
            raise serializers.ValidationError(
                {"origin": _("Origin and receiver must be different accounts")}
            )

        if origin:
            if origin.current_amount < data.get("amount"):
                raise serializers.ValidationError(
                    {"amount": _("Origin balance is less than the amount requested")}
                )
        return data

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(_("Amount must be greater than 0"))
        return amount


class AccountSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "identifier", "owner", "incomes", "payments", "current_amount")
        read_only_fields = ("incomes", "payments")
        expandable_fields = {
            "incomes": (
                TransactionSerializer,
                {"read_only": True, "many": True, "omit": ["receiver"]},
            ),
            "payments": (
                TransactionSerializer,
                {"read_only": True, "many": True, "omit": ["origin"]},
            ),
        }

    def create(self, validated_data):
        data = self.context.get("request").data
        income_transactions = data.get("incomes")
        if not income_transactions:
            raise serializers.ValidationError(
                {"incomes": _("You must specify an initial amount")}
            )
        account = Account.objects.create(**validated_data)
        for income in income_transactions:
            Transaction.objects.create(receiver=account, **income)
        return account
