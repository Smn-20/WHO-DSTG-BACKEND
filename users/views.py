from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from .models import *
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.http import HttpResponse,JsonResponse
import json
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
# Create your views here.

def custom_response(data=None, message='', status=True):
    return Response({
        'status': status,
        'message': message,
        'data': data if data is not None else {}
    })

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
                token, _ = Token.objects.get_or_create(user=user)
                response = {
                    'status': True,
                    'message': 'Login successful',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'roles': list(user.roles.values_list('name', flat=True)),
                        'token': str(token),
                        'code': status.HTTP_200_OK
                    }
                }
                return JsonResponse(response, status=status.HTTP_200_OK)
            else:
                response = {
                    'status': False,
                    'message': 'Email or password incorrect!',
                    'data': {}
                }
                return JsonResponse(response, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            response = {
                'status': False,
                'message': 'Email or password incorrect!',
                'data': {}
            }
            return JsonResponse(response, status=status.HTTP_200_OK)

    # Optional: handle non-POST requests
    return JsonResponse({
        'status': False,
        'message': 'Invalid request method',
        'data': {
            'code': status.HTTP_405_METHOD_NOT_ALLOWED
        }
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)



#Registration
def registration(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)

        try:
            if User.objects.filter(email=body['email']).exists():
                response = {
                    'status': False,
                    'message': 'A user with this email already exists!',
                    'data': {}
                }
                return JsonResponse(response, status=status.HTTP_200_OK)

            user = User.objects.create_user(
                email=body['email'],
                password=body['password'],
            )

            for role_id in body.get('roles', []):
                try:
                    role = Role.objects.get(id=role_id)
                    user.roles.add(role)
                except Role.DoesNotExist:
                    # Optional: handle missing role more gracefully
                    pass

            user.save()

            response = {
                'status': True,
                'message': 'Registered successfully!',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'roles': list(user.roles.values_list('name', flat=True)),
                    'code': status.HTTP_200_OK
                }
            }
            return JsonResponse(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = {
                'status': False,
                'message': 'Registration failed!',
                'data': {
                    'error': str(e),
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            }
            return JsonResponse(response, status=status.HTTP_200_OK)

    return JsonResponse({
        'status': False,
        'message': 'Invalid request method',
        'data': {
            'code': status.HTTP_405_METHOD_NOT_ALLOWED
        }
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)




class ConditionListView(ListAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response = {
            'status': True,
            'message': 'Conditions fetched successfully',
            'data': serializer.data
        }

        return Response(response, status=status.HTTP_200_OK)

class DepartmentListView(ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response = {
            'status': True,
            'message': 'Department fetched successfully',
            'data': serializer.data
        }

        return Response(response, status=status.HTTP_200_OK)

class DepartmentCreateView(CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            response = {
                'status': True,
                'message': 'Department created successfully',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': False,
            'message': 'Department creation failed',
            'data': serializer.errors
        }, status=status.HTTP_201_CREATED)


class ConditionBySymptoms(ListAPIView):
    serializer_class = ConditionSerializer
    queryset = Condition.objects.all()

    def get(self, request, *args, **kwargs):
        symptom_ids = request.query_params.get('symptom_ids')
        
        if not symptom_ids:
            return Response({
                'status': False,
                'message': 'No symptom IDs provided',
                'data': {
                    'code': status.HTTP_400_BAD_REQUEST
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            symptom_ids = [int(id.strip()) for id in symptom_ids.split(',')]
        except ValueError:
            return Response({
                'status': False,
                'message': 'Invalid symptom ID format',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        symptom_conditions = []
        for symptom_id in symptom_ids:
            conditions = Condition.objects.filter(symptoms__id=symptom_id)
            symptom_conditions.append(set(conditions))

        if symptom_conditions:
            common_conditions = set.intersection(*symptom_conditions)
        else:
            common_conditions = Condition.objects.none()

        serializer = ConditionSerializer(common_conditions, many=True)

        return Response({
            'status': True,
            'message': 'Conditions fetched successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class ConditionByDepartment(ListAPIView):
    serializer_class = ConditionSerializer

    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        print(department_id)
        return Condition.objects.filter(department=department_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'status': True,
            'message': 'Conditions fetched successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class ConditionCreateView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Condition.objects.all()

    def post(self, request):
        name = request.data.get('name')
        department_id = request.data.get('department')

        condition = Condition.objects.create(name=name, department_id=department_id)

        attributes = []
        i = 0
        while f'attributes[{i}][title]' in request.data:
            title = request.data.get(f'attributes[{i}][title]')
            content = request.data.get(f'attributes[{i}][content]')
            attr = Attribute.objects.create(condition=condition, title=title, content=content)

            j = 0
            while f'attributes[{i}][images][{j}][file]' in request.FILES:
                img_file = request.FILES.get(f'attributes[{i}][images][{j}][file]')
                img_type = request.data.get(f'attributes[{i}][images][{j}][type]')
                img_title = request.data.get(f'attributes[{i}][images][{j}][title]')
                AttributeImage.objects.create(attribute=attr, image=img_file, type=img_type, title=img_title)
                j += 1

            i += 1

        return Response({'status': True, 'message': 'Condition created successfully', 'data':{}})


class ForumPostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = ForumPost.objects.all().order_by('-created_at')
        serializer = ForumPostSerializer(posts, many=True)
        return custom_response(data=serializer.data, message="Posts retrieved successfully.")

    def post(self, request):
        post = ForumPost.objects.create(user=request.user, content=request.data.get('content'))
        serializer = ForumPostSerializer(post)
        return custom_response(data=serializer.data, message='Post created successfully.')

class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(ForumPost, id=post_id)
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=request.data.get('content')
        )
        serializer = CommentSerializer(comment)
        return custom_response(data=serializer.data, message='Comment added.')

class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(ForumPost, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return custom_response(message='Like removed.')
        else:
            return custom_response(message='Post liked.')



class SymptomListView(ListAPIView):
    queryset = Symptoms.objects.all()
    serializer_class = SymptomSerializer

class SymptomCreateView(CreateAPIView):
    queryset = Symptoms.objects.all()
    serializer_class = SymptomSerializer

class SymptomRetrieveView(RetrieveAPIView):
    queryset = Symptoms.objects.all()
    serializer_class = SymptomSerializer2
    lookup_field = 'id'

class ConditionRetrieveView(RetrieveAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer2
    lookup_field = 'id'

class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    model = User
    # permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return User.objects.get(id=self.request.data['user_id'])

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({
                    'status': False,
                    'message': 'Wrong password',
                    'data': {
                        'errors': {'old_password': ['Wrong password.']}
                    }
                }, status=status.HTTP_200_OK)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response({
                'status': True,
                'message': 'Password updated successfully',
                'data': {}
            }, status=status.HTTP_200_OK)

        return Response({
            'status': False,
            'message': 'Password update failed',
            'data': {
                'errors': serializer.errors
            }
        }, status=status.HTTP_200_OK)
            