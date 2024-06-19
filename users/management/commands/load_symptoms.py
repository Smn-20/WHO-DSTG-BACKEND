import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Symptoms, Condition

class Command(BaseCommand):
    help = 'Load symptoms data from Excel file into database'

    def handle(self, *args, **kwargs):
        # Get the path to the current directory where this script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the Excel file
        file_path = os.path.join(base_dir, 'symptoms_data.xlsx')
        
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Iterate over the DataFrame and create Symptoms objects
        for index, row in df.iterrows():
            # Create the Symptoms object
            symptom = Symptoms.objects.create(
                name=row['name'],
                further_management="",
                referral_criteria=""
            )
            
            # Get the list of condition IDs from the comma-separated string
            condition_ids = [int(id_.strip()) for id_ in str(row['conditions']).split(',')]
            
            # Add the Conditions to the Symptoms object
            for condition_id in condition_ids:
                try:
                    condition = Condition.objects.get(id=condition_id)
                    symptom.conditions.add(condition)
                except Condition.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Condition with id {condition_id} does not exist'))
            
            symptom.save()
        
        self.stdout.write(self.style.SUCCESS('Symptoms data successfully loaded'))
