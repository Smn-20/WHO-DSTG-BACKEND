import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Symptoms, GroupSymptom

class Command(BaseCommand):
    help = 'Create GroupSymptoms from Excel columns and assign existing Symptoms to them'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'my_symptoms_grouped.xlsx')

        # Read all sheets
        excel_data = pd.read_excel(file_path, sheet_name=None, header=0)

        for sheet_name, sheet_df in excel_data.items():
            self.stdout.write(self.style.SUCCESS(f"Processing sheet: {sheet_name}"))

            for column in sheet_df.columns:
                group_name = str(column).strip()
                if not group_name:
                    continue

                group, _ = GroupSymptom.objects.get_or_create(name=group_name)

                for cell in sheet_df[column].dropna():
                    symptom_text = str(cell).strip()
                    if not symptom_text:
                        continue

                    matched_symptoms = Symptoms.objects.filter(name__iexact=symptom_text)

                    if not matched_symptoms.exists():
                        matched_symptoms = Symptoms.objects.filter(name__icontains=symptom_text)

                    if matched_symptoms.exists():
                        for symptom in matched_symptoms:
                            symptom.group.add(group)
                            symptom.save()
                        self.stdout.write(self.style.SUCCESS(f"Linked symptom(s) '{symptom_text}' to group '{group_name}'"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Symptom '{symptom_text}' not found in DB."))

        self.stdout.write(self.style.SUCCESS('Group symptoms creation and assignment completed.'))
