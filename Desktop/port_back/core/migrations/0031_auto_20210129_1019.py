from django.db import migrations


def add_auth_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).create(id=9, name="Глава буксирной компании")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0030_auto_20210128_0758'),
    ]

    operations = [
        migrations.RunPython(add_auth_group),
    ]
