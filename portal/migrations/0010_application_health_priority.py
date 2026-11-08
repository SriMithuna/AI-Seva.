from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0009_emailotp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="priority",
            field=models.CharField(
                choices=[
                    ("Documents Pending", "Documents Pending"),
                    ("Critical", "Critical"),
                    ("High", "High"),
                    ("Medium", "Medium"),
                    ("Low", "Low"),
                ],
                default="Low",
                max_length=20,
            ),
        ),
    ]
