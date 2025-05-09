import re
from django.core.management.base import BaseCommand
from users.models import Attribute

class Command(BaseCommand):
    help = "Replace ' • ' with HTML or plain text line breaks depending on content type."

    def handle(self, *args, **kwargs):
        updated = 0
        # Matches: ' • ' between two letters
        pattern = re.compile(r'(?<=[a-zA-Z]) • (?=[a-zA-Z])')

        for attr in Attribute.objects.all():
            original_content = attr.content

            if '</p>' in original_content:
                # Use HTML line break
                new_content = pattern.sub('<br>•&nbsp;', original_content)
            else:
                # Use plain text line break
                new_content = pattern.sub('\r\n•\t', original_content)

            if new_content != original_content:
                attr.content = new_content
                attr.save()
                updated += 1
                self.stdout.write(f"Updated Attribute ID {attr.id}")

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} Attribute records.'))
