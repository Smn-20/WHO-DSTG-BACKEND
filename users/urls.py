from django.urls import path,include
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('users',UserListView.as_view()),
    path('roles',RoleListView.as_view()),
    path('create-condition',ConditionCreateView.as_view()),
    path('edit-condition/<int:pk>', ConditionEditView.as_view()),
    path('edit-department/<int:pk>', DepartmentUpdateView.as_view()),
    path('create-symptom/',SymptomCreateView.as_view()),
    path('conditions/',ConditionListView.as_view()),
    path('departments/',DepartmentListView.as_view()),
    path('create-department',DepartmentCreateView.as_view()),
    path('symptoms/',SymptomListView.as_view()),
    path('symptom/<id>/',SymptomRetrieveView.as_view()),
    path('condition/<id>/',ConditionRetrieveView.as_view()),
    path('create-user',csrf_exempt(create_user)),
    path('edit-user/<int:user_id>', csrf_exempt(edit_user)),
    path('login',csrf_exempt(login)),
    path('change-password', ChangePasswordView.as_view()),
    path('conditions-by-symptoms', ConditionBySymptoms.as_view()),
    path('symptoms-by-department', SymptomsByDepartment.as_view()),
    path('conditions-by-department/<int:department_id>/', ConditionByDepartment.as_view()),
    path('forum', ForumPostListCreateView.as_view(), name='forum_list_create'),
    path('forum/<int:post_id>/comment', CommentCreateView.as_view()),
    path('forum/<int:post_id>/like-toggle', LikeToggleView.as_view()),
]