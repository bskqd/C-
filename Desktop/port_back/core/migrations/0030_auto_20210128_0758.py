from django.db import migrations


def add_auth_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).bulk_create([
        Group(id=7, name='Пограничная служба'),
        Group(id=8, name='Диспетчер порта')
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_borderguard_portmanager_squashed_0030_auto_20210127_1326'),
    ]

    operations = [
        migrations.RunPython(add_auth_groups),
    ]
