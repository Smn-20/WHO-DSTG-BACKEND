from django.core.management.base import BaseCommand
from users.models import Attribute

class Command(BaseCommand):
    help = 'Replace  or o with • in Attribute content fields.'

    def handle(self, *args, **kwargs):
        updated = 0

        # Fetch all attributes
        attributes = Attribute.objects.all()

        for attr in attributes:
            original_content = attr.content
            new_content = original_content.replace('', '•').replace(' o ', ' • ').replace('\no ', '\n•').replace('\to ', '\t•')

            if new_content != original_content:
                attr.content = new_content
                attr.save()
                updated += 1
                self.stdout.write(f"Updated Attribute ID {attr.id}: replaced special characters.")

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} Attribute records with new bullet format.'))
