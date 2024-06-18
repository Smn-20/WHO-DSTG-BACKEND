from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView,DestroyAPIView,UpdateAPIView
from .models import *
from .serializers import *
from django.http import HttpResponse,JsonResponse
import json
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
# Create your views here.

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoleListView(ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer





#Authentication
def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        try:
            user = User.objects.get(email=body['email'])
            if user.check_password(body['password']):
                token = Token.objects.get_or_create(user=user)[0]
                data = {
                    'user_id': user.id,
                    'email': user.email,
                    'status': 'success',
                    'roles':str(list(user.roles.values_list('name', flat=True))),
                    'token': str(token),
                    'code': status.HTTP_200_OK,
                    'message': 'Login successfull',
                    'data': []
                }
                dump = json.dumps(data)
                return HttpResponse(dump, content_type='application/json')
            else:
                data = {
                    'status': 'failure',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Email or password incorrect!',
                    'data': []
                }
                dump = json.dumps(data)
                return HttpResponse(dump, content_type='application/json')
        except User.DoesNotExist:
            data = {
                'status': 'failure',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Email or password incorrect!',
                'data': []
            }
            dump = json.dumps(data)
            return HttpResponse(dump, content_type='application/json')



#Registration
def registration(request):
    if request.method=='POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        try:
            user=User.objects.get(email=body['email'])
            data = {
                'result': 'A user with this email already exists!',
            }
            dump = json.dumps(data)
            return HttpResponse(dump, content_type='application/json')
        except User.DoesNotExist:
            user=User.objects.create_user(
                email=body['email'],
                password=body['password'],
                )
            for role in body['roles']:
                role=Role.objects.get(id=role)
                user.roles.add(role)
            
            user.save()
            data = {
                'name': 'Registered successfully!!',
            }
            dump = json.dumps(data)
            return HttpResponse(dump, content_type='application/json')




class ConditionListView(ListAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer


class ConditionCreateView(CreateAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer


class SymptomListView(ListAPIView):
    queryset = Symptoms.objects.all()
    serializer_class = SymptomSerializer


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    model = User
    # permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = User.objects.get(id=self.request.data['user_id'])
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            