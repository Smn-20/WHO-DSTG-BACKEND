import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Condition, Attribute, Department

class Command(BaseCommand):
    help = 'Load conditions and their attributes from an Excel file into the database.'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'conditions1.xlsx')

        # Load the Excel file with all sheets
        xl = pd.ExcelFile(file_path)

        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name, header=None)

            if df.empty:
                continue

            # Get condition name
            condition_name = str(df.iloc[0, 0]).strip()
            if not condition_name:
                continue

            condition, created = Condition.objects.get_or_create(name=condition_name)

            # Assign department with id=8 if condition was created
            if created:
                try:
                    department = Department.objects.get(id=8)
                    condition.department = department
                    condition.save()
                except Department.DoesNotExist:
                    self.stdout.write(self.style.WARNING("Department with id=8 does not exist. Skipping department assignment."))

            # Check if there are enough rows for titles and contents
            if df.shape[0] < 3:
                self.stdout.write(self.style.WARNING(f"Sheet '{sheet_name}' does not have enough rows. Skipped."))
                continue

            titles = df.iloc[1]
            contents = df.iloc[2]

            for title, content in zip(titles, contents):
                if pd.notna(title) and pd.notna(content):
                    Attribute.objects.create(
                        condition=condition,
                        title=str(title).strip(),
                        content=str(content).strip()
                    )

        self.stdout.write(self.style.SUCCESS('All conditions and attributes successfully loaded from all sheets.'))