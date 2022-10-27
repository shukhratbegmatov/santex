from django.core.management.base import BaseCommand

from common.management.districts import districts
from common.models import District, Region


class Command(BaseCommand):
    help = 'import districts'

    def handle(self, *args, **kwargs):
        for district in districts:
            try:
                region = Region.objects.get(name=district.get("region"))
            except Region.DoesNotExist:
                region = Region.objects.create(name=district.get("region"))
            District.objects.update_or_create(
                region=region, name=district.get("name_uz"), defaults={"name_ru": district.get("name_ru")}
            )

        self.stdout.write(self.style.SUCCESS('Successfully added districts'))
