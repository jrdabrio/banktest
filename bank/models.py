from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_currentuser.db.models import CurrentUserField


class Authorable(models.Model):
    """Add auto populated control fields"""

    creation_datetime = models.DateTimeField(
        _("Creation date"), auto_now_add=True, editable=False
    )
    modification_datetime = models.DateTimeField(
        _("Modification date"), auto_now=True, editable=False
    )

    creation_user = CurrentUserField(
        blank=True,
        verbose_name=_("Creation user"),
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_creations",
    )
    modification_user = CurrentUserField(
        on_update=True,
        blank=True,
        verbose_name=_("Modification user"),
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_modifications",
    )

    class Meta:
        abstract = True


class Customer(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)

    def __str__(self) -> str:
        return self.name


class Account(Authorable):
    identifier = models.CharField(
        verbose_name=_("Identifier"), max_length=50, unique=True
    )
    owner = models.ForeignKey(
        Customer,
        verbose_name=_("Owner"),
        related_name="accounts",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.identifier

    @property
    def total_incomes(self) -> float:
        if self.incomes.exists():
            account_incomes = self.incomes.aggregate(total_incomes=models.Sum("amount"))
            return account_incomes.get("total_incomes")
        return 0

    @property
    def total_payments(self) -> float:
        if self.payments.exists():
            account_payments = self.payments.aggregate(
                total_payments=models.Sum("amount")
            )
            return account_payments.get("total_payments")
        return 0

    @property
    def current_amount(self) -> float:
        return self.total_incomes - self.total_payments


class Transaction(Authorable):
    """
    Transactions related to an Account. At least one of the Account fields must be filled
    """

    concept = models.CharField(
        verbose_name=_("Concept"), max_length=255, blank=True, null=True
    )
    amount = models.FloatField(
        verbose_name=_("Amount"), validators=[MinValueValidator(0.01)]
    )
    origin = models.ForeignKey(
        Account,
        verbose_name=_("Origin"),
        related_name="payments",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    receiver = models.ForeignKey(
        Account,
        verbose_name=_("Receiver"),
        related_name="incomes",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="origin_or_receiver_required",
                check=models.Q(origin=True) | models.Q(receiver=True),
            )
        ]

    def __str__(self) -> str:
        str_value = f"Amount: {self.amount}"
        if self.concept:
            str_value += f" Concept: {self.concept}"
        return str_value
