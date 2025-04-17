import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Condition, Attribute

class Command(BaseCommand):
    help = 'Load conditions and their attributes from an Excel file into the database.'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'conditions1.xlsx')

        # Load the Excel file with all sheets
        xl = pd.ExcelFile(file_path)

        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name, header=None)

            # Skip empty sheets
            if df.empty:
                continue

            # Extract condition name from first cell (A1)
            condition_name = str(df.iloc[0, 0]).strip()
            if not condition_name:
                continue

            condition, _ = Condition.objects.get_or_create(name=condition_name)

            # Extract attribute titles from second row (index 1)
            # Extract attribute contents from third row (index 2)
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
