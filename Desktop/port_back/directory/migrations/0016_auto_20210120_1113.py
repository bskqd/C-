from django.db import migrations


def add_test_port(apps, schema_editor):
    Port = apps.get_model("directory", "Port")
    db_alias = schema_editor.connection.alias
    Port.objects.using(db_alias).create(name='Test port', is_disable=True,
                                        position_capitan_ukr='Капітан Тестового порту',
                                        position_capitan_eng='Harbour Master of Test port',
                                        phone='111111', email=None, harbor_master_id=None, id=100)


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0015_port_harbor_master'),
    ]

    operations = [
        migrations.RunPython(add_test_port),
    ]
