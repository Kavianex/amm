# Generated by Django 4.1.7 on 2023-03-16 13:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('amm', '0002_remove_exchange_test_net_exchange_main_net'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchange',
            name='remark',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('side', models.CharField(blank=True, default='BUY', max_length=20, null=True)),
                ('symbol', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('base', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('quote', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('quantity', models.FloatField(blank=True, default=0, null=True)),
                ('quote_value', models.FloatField(blank=True, default=0, null=True)),
                ('order_type', models.CharField(blank=True, default='MARKET', max_length=20, null=True)),
                ('order_id', models.CharField(blank=True, default='', max_length=46, null=True)),
                ('client_id', models.CharField(blank=True, default='', max_length=46, null=True)),
                ('price', models.FloatField(blank=True, default=0, null=True)),
                ('stop_price', models.FloatField(blank=True, default=0, null=True)),
                ('stop_limit_price', models.FloatField(blank=True, default=0, null=True)),
                ('filled_quote', models.FloatField(blank=True, default=0, null=True)),
                ('filled_base', models.FloatField(blank=True, default=0, null=True)),
                ('status', models.CharField(blank=True, default='NEW', max_length=20, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('insert_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('update_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('exchange', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='amm.exchange')),
            ],
        ),
    ]
