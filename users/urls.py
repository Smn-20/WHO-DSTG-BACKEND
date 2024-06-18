from django.urls import path,include
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('users/',UserListView.as_view()),
    path('create-condition/',ConditionCreateView.as_view()),
    path('create-symptom/',SymptomCreateView.as_view()),
    path('conditions/',ConditionListView.as_view()),
    path('symptoms/',SymptomListView.as_view()),
    path('symptom/<id>/',SymptomRetrieveView.as_view()),
    path('register/',csrf_exempt(registration)),
    path('login/',csrf_exempt(login)),
    path('change-password/', ChangePasswordView.as_view()),
    path('conditions-by-symptoms/', ConditionBySymptoms.as_view()),
]