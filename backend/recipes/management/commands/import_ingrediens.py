import os
import json

from django.core.management.base import BaseCommand

from recipes import models

data = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath("data")))
)

print (data)

class Command(BaseCommand):
    def handle(self, *args, **options):
        models.Ingredient.objects.all().delete()
        with open(f"{data}/foodgram-project-react/data/ingredients.json", "r") as j:
            data_dict = json.loads(j.read())
            print ('всего записей', )
            count = 0
            try:
                for record in data_dict:
                    count += 1
                    name = record.get("name")
                    measurement_unit=record.get("measurement_unit")
                    try:
                        models.Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    except:
                        print ('Ошибка импорта', record)
                    
                print("Загрузка ингридиентов завершена! "
                      f"Загружено товаров: {models.Ingredient.objects.all().count()}")
            except Exception as er:
                print("Что-то не так с моделями, путями или базой данных "
                      f"проверьте, ошибка: {er}")