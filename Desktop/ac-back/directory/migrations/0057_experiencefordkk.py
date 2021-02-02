from django.db import migrations


def update_experience(apps, schema_editor):
    ExperinceForDKK = apps.get_model('directory', 'ExperinceForDKK')
    exp = ExperinceForDKK.objects.get(position_id=87, month_required=36)
    exp.experince_value = [
        {"month": [6], "column": "X2", "function": [13], "is_gmzlb": False,
         "position": [16, 17, 18, 19, 20, 22, 47, 58], "required": False,
         "type_vessel": [2, 1, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45],
         "gross_capacity": [500], "practical_book": "any", "electrical_power": "any", "propulsion_power": [750],
         "levelRefrigerPlant": "any", "mode_of_navigation": "any", "refrigerating_power": ""},
        {"month": [0], "column": "X1", "is_gmzlb": False, "position": [16, 17, 18, 19, 20, 22, 47, 58],
         "type_vessel": [2, 1, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45],
         "required": False, "gross_capacity": [81], "practical_book": "any", "electrical_power": "any",
         "propulsion_power": [56], "levelRefrigerPlant": "any", "mode_of_navigation": "any",
         "refrigerating_power": ""}]
    exp.save(update_fields=['experince_value'])


class Migration(migrations.Migration):
    dependencies = [
        ('directory', '0056_typeofaccrualrules_type_sailor'),
    ]

    operations = [
        migrations.RunPython(update_experience)
    ]
