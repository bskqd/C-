from django.db import migrations


def add_auth_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).create(id=10, name="Капитан буксира")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0032_auto_20210129_1024_squashed_0033_auto_20210129_1104'),
    ]

    operations = [
        migrations.RunPython(add_auth_group),
    ]
