import os
import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Condition

class Command(BaseCommand):
    help = 'Load data from Excel file into database'

    def handle(self, *args, **kwargs):
        # Get the path to the current directory where this script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the Excel file
        file_path = os.path.join(base_dir, 'conditions_data.xlsx')
        
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Iterate over the DataFrame and create Condition objects
        for index, row in df.iterrows():
            Condition.objects.create(
                name=row['name'],
                description=row['description'],
                causes=row['causes'],
                symptoms_features=row['symptoms_features'],
                investigations=row['investigations'],
                treatments=row['treatments'],
                surgical_options=row['surgical_options'],
                preventive_measures=row['preventive_measures'],
                emergency_management=row['emergency_management'],
                referral_criteria=row['referral_criteria'],
                prognosis=row['prognosis']
            )
        
        self.stdout.write(self.style.SUCCESS('Data successfully loaded'))
