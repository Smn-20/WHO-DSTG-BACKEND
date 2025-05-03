from django.core.management.base import BaseCommand
from users.models import Symptoms
import pandas as pd


class Command(BaseCommand):
    help = "Export symptom names to an Excel file"

    def handle(self, *args, **kwargs):
        symptoms = Symptoms.objects.values_list('name', flat=True)

        df = pd.DataFrame(symptoms, columns=["Symptom Name"])
        df.to_excel("my_symptoms.xlsx", index=False)

        self.stdout.write(self.style.SUCCESS("✅ Symptoms exported to symptoms.xlsx"))
