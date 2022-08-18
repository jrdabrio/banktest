from django.db.models import Q

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_flex_fields.views import FlexFieldsModelViewSet

from ..models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer


class AccountViewSet(FlexFieldsModelViewSet):
    """
    To create a new account you just need to do a post to the list endpoint with the following structure

    {
        "identifier": "ES12 3456 888888",
        "owner": 1,
        "incomes": [
            {
                "concept": "Initial amount",
                "amount": 2000
            }
        ]
    }
    """

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    search_fields = ("identifier",)
    ordering_fields = ("id", "identifier")
    ordering = ("-id",)
    permit_list_expands = ("incomes", "payments")

    @action(detail=True, methods=["post"])
    def transfer_amount(self, request, pk) -> Response:
        """
        Creates a transaction between the requested account and another given in the POST data.
        The account called in the url data will be used as origin
        """
        account = self.get_object()
        serializer = TransactionSerializer(data={"origin": account.pk, **request.data})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

    @action(detail=True)
    def balance(self, request, pk) -> Response:
        account = self.get_object()
        return Response(
            {
                "payments": account.total_payments,
                "incomes": account.total_incomes,
                "current_balance": account.current_amount,
            }
        )

    @action(detail=True)
    def history(self, request, pk) -> Response:
        """
        Return all the transactions related to the account in the URL
        """
        transaction_history = Transaction.objects.filter(
            Q(origin_id=pk) | Q(receiver_id=pk)
        ).order_by("-creation_datetime")
        serializer = TransactionSerializer(transaction_history, many=True)
        return Response(serializer.data)
