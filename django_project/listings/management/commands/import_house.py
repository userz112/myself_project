import csv
from django.core.management.base import BaseCommand
from listings.models import HouseListing


class Command(BaseCommand):
    help = '从 house_message.csv 导入房源数据'

    def handle(self, *args, **options):
        path = 'house_message.csv'
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            count = 0
            for row in reader:
                HouseListing.objects.create(
                    city=row[0],
                    house_name=row[1],
                    house_address=row[2],
                    house_description=row[3],
                    house_type=row[4],
                    house_size=row[5],
                    house_height=row[6],
                    house_position=row[7],
                    total_price=row[8],
                    unit_price=row[9],
                    house_image=row[10] if len(row) > 10 else "house_image/house_default.jpg",
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'成功导入 {count} 条房源数据'))
