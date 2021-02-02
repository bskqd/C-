from django.db import migrations


def add_test_ports_2(apps, schema_editor):
    Port = apps.get_model("directory", "Port")
    db_alias = schema_editor.connection.alias
    Port.objects.using(db_alias).bulk_create([Port(name='Test port PM', is_disable=True,
                                                   position_capitan_ukr='Капітан Тестового порту (PM)',
                                                   position_capitan_eng='Harbour Master of Test port (PM)',
                                                   phone='111111', email=None, harbor_master_id=None, id=101),
                                              Port(name='Test port BE', is_disable=True,
                                                   position_capitan_ukr='Капітан Тестового порту (BE)',
                                                   position_capitan_eng='Harbour Master of Test port (BE)',
                                                   phone='111111', email=None, harbor_master_id=None, id=102),
                                              Port(name='Test port FE', is_disable=True,
                                                   position_capitan_ukr='Капітан Тестового порту (FE)',
                                                   position_capitan_eng='Harbour Master of Test port (FE)',
                                                   phone='111111', email=None, harbor_master_id=None, id=103),
                                              Port(name='Test port QA', is_disable=True,
                                                   position_capitan_ukr='Капітан Тестового порту (QA)',
                                                   position_capitan_eng='Harbour Master of Test port (QA)',
                                                   phone='111111', email=None, harbor_master_id=None, id=104)
                                              ])


class Migration(migrations.Migration):
    dependencies = [
        ('directory', '0017_auto_20210121_0722'),
    ]

    operations = [
        migrations.RunPython(add_test_ports_2),
    ]
