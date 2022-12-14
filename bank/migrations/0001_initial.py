# Generated by Django 3.2.14 on 2022-08-15 16:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_datetime', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('identifier', models.CharField(max_length=50, unique=True, verbose_name='Identifier')),
                ('creation_user', django_currentuser.db.models.fields.CurrentUserField(blank=True, default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bank_account_creations', to=settings.AUTH_USER_MODEL, verbose_name='Creation user')),
                ('modification_user', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.PROTECT, on_update=True, related_name='bank_account_modifications', to=settings.AUTH_USER_MODEL, verbose_name='Modification user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_datetime', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('concept', models.CharField(blank=True, max_length=255, null=True, verbose_name='Concept')),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Amount')),
                ('creation_user', django_currentuser.db.models.fields.CurrentUserField(blank=True, default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bank_transaction_creations', to=settings.AUTH_USER_MODEL, verbose_name='Creation user')),
                ('modification_user', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.PROTECT, on_update=True, related_name='bank_transaction_modifications', to=settings.AUTH_USER_MODEL, verbose_name='Modification user')),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='bank.account', verbose_name='Origin')),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='incomes', to='bank.account', verbose_name='Receiver')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accounts', to='bank.customer', verbose_name='Owner'),
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.CheckConstraint(check=models.Q(('origin', True), ('receiver', True), _connector='OR'), name='origin_or_receiver_required'),
        ),
    ]
