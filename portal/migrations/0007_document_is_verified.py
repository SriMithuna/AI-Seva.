from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_application_extra_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
    ]
