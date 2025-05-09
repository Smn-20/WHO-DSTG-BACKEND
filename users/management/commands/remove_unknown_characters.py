from django.core.management.base import BaseCommand
from users.models import Attribute

class Command(BaseCommand):
    help = "Replace ' • ' with <br>•&nbsp; or \\r\\n•\\t depending on whether </p> is in the content."

    def handle(self, *args, **kwargs):
        updated = 0

        for attr in Attribute.objects.all():
            original_content = attr.content

            if '</p>' in original_content:
                new_content = original_content.replace(' • ', '<br>•&nbsp;')
            else:
                new_content = original_content.replace(' • ', '\r\n•\t')

            if new_content != original_content:
                attr.content = new_content
                attr.save()
                updated += 1
                self.stdout.write(f"Updated Attribute ID {attr.id}")

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} Attribute records.'))
