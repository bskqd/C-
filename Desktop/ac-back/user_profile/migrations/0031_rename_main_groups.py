from django.db import migrations


def rename_agent(apps, schema_editor):
    MainGroups = apps.get_model('user_profile', 'MainGroups')
    MainGroups.objects.filter(name='Агент').update(name='Довірена особа')
    StatusDocument = apps.get_model('directory', 'StatusDocument')
    StatusDocument.objects.filter(name_ukr='Видалено агентом').update(name_ukr='Видалено',
                                                                      name_eng='Removed')
    StatusDocument.objects.filter(name_ukr='Створено агентом').update(name_ukr='Створено довіреною особою',
                                                                      name_eng='Created by seaman')


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0030_auto_20201207_1627'),
    ]

    operations = [
        migrations.RunPython(rename_agent)
    ]
