from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0007_document_is_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="priority_group_verified",
            field=models.BooleanField(default=False),
        ),
    ]
