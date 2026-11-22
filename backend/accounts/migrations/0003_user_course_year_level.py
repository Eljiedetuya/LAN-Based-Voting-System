from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_must_change_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='course',
            field=models.CharField(blank=True, choices=[('BSIT', 'BSIT'), ('BIT', 'BIT')], default='', max_length=4),
        ),
        migrations.AddField(
            model_name='user',
            name='year_level',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')], null=True),
        ),
    ]
