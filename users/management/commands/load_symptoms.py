import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Symptoms, Condition

class Command(BaseCommand):
    help = 'Load symptoms from Excel sheets into the database'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'dentistry_symptoms.xlsx')

        # Read all sheets
        excel_data = pd.read_excel(file_path, sheet_name=None, header=None)

        for sheet_name, sheet_df in excel_data.items():
            if sheet_df.shape[0] < 3:
                self.stdout.write(self.style.WARNING(f"Sheet '{sheet_name}' does not have enough rows. Skipping."))
                continue

            condition_name = str(sheet_df.iloc[0, 0]).strip()
            try:
                condition = Condition.objects.get(name__iexact=condition_name)
            except Condition.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Condition '{condition_name}' does not exist. Skipping sheet."))
                continue

            symptoms_row = str(sheet_df.iloc[2, 0])
            symptoms = [sym.strip().strip('#') for sym in symptoms_row.split('#') if sym.strip()]
            
            for symptom_name in symptoms:
                symptom, created = Symptoms.objects.get_or_create(name=symptom_name)
                symptom.conditions.add(condition)
                symptom.save()
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{action} symptom '{symptom_name}' for condition '{condition_name}'"))

        self.stdout.write(self.style.SUCCESS('All symptoms processed successfully.'))

