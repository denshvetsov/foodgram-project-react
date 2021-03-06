import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

data = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath("data")))
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        Ingredient.objects.all().delete()
        with open(
            f"{data}/foodgram-project-react/data/ingredients.json",
            "r"
        ) as j:
            data_dict = json.loads(j.read())
            print('всего записей', )
            count = 0
            try:
                for record in data_dict:
                    count += 1
                    name = record.get("name")
                    measurement_unit = record.get("measurement_unit")
                    try:
                        Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    except Exception as error:
                        print('Ошибка импорта', record, error)

                print(
                    f"Загрузка ингредиентов завершена! "
                    f"Загружено товаров: "
                    f"{Ingredient.objects.all().count()}"
                )
            except Exception as error:
                print("Что-то не так с моделями, путями или базой данных "
                      f"проверьте, ошибка: {error}")
