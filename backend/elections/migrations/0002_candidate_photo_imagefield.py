from django.db import migrations, models
import elections.models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='photo_path',
            field=models.ImageField(blank=True, max_length=255, upload_to=elections.models.candidate_photo_path),
        ),
    ]
