from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from .models import *
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.http import HttpResponse,JsonResponse
import json
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, AllowAny
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
def create_user(request):
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
                names=body['names'],
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


def edit_user(request, user_id):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            print(body)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': False,
                    'message': 'User not found',
                    'data': {
                        'code': status.HTTP_404_NOT_FOUND
                    }
                }, status=status.HTTP_200_OK)

            # Optional: check if email is changing and if it's already taken
            new_email = body.get('email')
            if new_email and new_email != user.email:
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'status': False,
                        'message': 'Email is already taken by another user.',
                        'data': {}
                    }, status=status.HTTP_200_OK)
                user.email = new_email

            # Update roles if provided
            if 'roles' in body:
                user.roles.clear()
                for role_id in body['roles']:
                    try:
                        role = Role.objects.get(id=role_id)
                        user.roles.add(role)
                    except Role.DoesNotExist:
                        pass

            if 'names' in body:
                user.names = body['names']
            user.save()

            return JsonResponse({
                'status': True,
                'message': 'User updated successfully',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'roles': list(user.roles.values_list('name', flat=True)),
                    'code': status.HTTP_200_OK
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({
                'status': False,
                'message': 'Update failed!',
                'data': {
                    'error': str(e),
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            }, status=status.HTTP_200_OK)

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

class DepartmentUpdateView(APIView):
    queryset = Department.objects.all()
    def post(self, request, pk, *args, **kwargs):
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': 'Department updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status': False,
            'message': 'Department update failed',
            'data': serializer.errors
        }, status=status.HTTP_200_OK)



class ConditionBySymptoms(ListAPIView):
    serializer_class = ConditionSerializer
    queryset = Condition.objects.all()

    def get(self, request, *args, **kwargs):
        symptom_ids = request.query_params.get('symptom_ids')

        if not symptom_ids:
            return Response({
                'status': False,
                'message': 'No symptom IDs provided',
                'data': {'code': status.HTTP_400_BAD_REQUEST}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            symptom_ids = [int(id.strip()) for id in symptom_ids.split(',')]
        except ValueError:
            return Response({
                'status': False,
                'message': 'Invalid symptom ID format',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get original symptoms and their groups
        input_symptoms = Symptoms.objects.filter(id__in=symptom_ids).prefetch_related('group', 'conditions')
        related_groups = GroupSymptom.objects.filter(symptoms__in=input_symptoms).distinct()

        # Get all symptoms in those groups
        group_symptoms = Symptoms.objects.filter(group__in=related_groups).distinct()

        # Combine input symptoms and group-related symptoms
        all_considered_symptoms = set(input_symptoms) | set(group_symptoms)

        # Fetch all conditions linked to these symptoms
        candidate_conditions = Condition.objects.filter(symptoms__in=all_considered_symptoms).distinct()

        # Filter conditions: only return those that are linked to *at least one symptom from each input symptom or its group*
        valid_conditions = []
        for condition in candidate_conditions:
            condition_symptoms = set(condition.symptoms.all())
            match = True
            for original_symptom in input_symptoms:
                # Include all symptoms in the same group as current original symptom
                group_symptom_set = set(Symptoms.objects.filter(group__in=original_symptom.group.all()))
                # Check if any symptom from this group (or itself) exists in condition's symptoms
                if not (group_symptom_set | {original_symptom}) & condition_symptoms:
                    match = False
                    break
            if match:
                valid_conditions.append(condition)

        serializer = self.get_serializer(valid_conditions, many=True)
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



class SymptomsByDepartment(ListAPIView):
    serializer_class = SymptomSerializer
    queryset = Symptoms.objects.all()

    def get(self, request, *args, **kwargs):
        department_id = request.query_params.get('department_id')

        if not department_id:
            return Response({
                'status': False,
                'message': 'No department ID provided',
                'data': {'code': status.HTTP_400_BAD_REQUEST}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            department_id = int(department_id)
        except ValueError:
            return Response({
                'status': False,
                'message': 'Invalid department ID format',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Prefetch conditions and their departments in a single query
        symptoms = Symptoms.objects.prefetch_related(
            Prefetch('conditions', queryset=Condition.objects.select_related('department'))
        ).filter(conditions__department__id=department_id).distinct()

        serializer = self.get_serializer(symptoms, many=True)
        return Response({
            'status': True,
            'message': 'Symptoms fetched successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)



class ConditionCreateView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Condition.objects.all()

    def post(self, request):
        try:
            name = request.data.get('name')
            department_id = request.data.get('department')

            if not name or not department_id:
                return Response({'status': False, 'message': 'Missing required fields: name or department'}, status=status.HTTP_200_OK)

            condition = Condition.objects.create(name=name, department_id=department_id)

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

            return Response({'status': True, 'message': 'Condition created successfully', 'data': {}}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': False, 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_200_OK)



class ConditionEditView(APIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Condition.objects.all()

    def post(self, request, pk):
        try:
            condition = Condition.objects.get(pk=pk)
            name = request.data.get('name')
            department_id = request.data.get('department')

            if not name or not department_id:
                return Response({'status': False, 'message': 'Missing required fields: name or department'}, status=status.HTTP_200_OK)

            condition.name = name
            condition.department_id = department_id
            condition.save()

            received_attr_ids = []
            i = 0
            while f'attributes[{i}][title]' in request.data:
                attr_id = request.data.get(f'attributes[{i}][id]')
                title = request.data.get(f'attributes[{i}][title]')
                content = request.data.get(f'attributes[{i}][content]')

                if attr_id:
                    attr = Attribute.objects.get(id=attr_id, condition=condition)
                    attr.title = title
                    attr.content = content
                    attr.save()
                else:
                    attr = Attribute.objects.create(condition=condition, title=title, content=content)

                received_attr_ids.append(attr.id)

                received_img_ids = []
                j = 0
                while f'attributes[{i}][images][{j}][title]' in request.data:
                    img_id = request.data.get(f'attributes[{i}][images][{j}][id]')
                    img_title = request.data.get(f'attributes[{i}][images][{j}][title]')
                    img_type = request.data.get(f'attributes[{i}][images][{j}][type]')
                    img_file = request.FILES.get(f'attributes[{i}][images][{j}][file]')
                    img_url = request.data.get(f'attributes[{i}][images][{j}][image]')
                    if img_id:
                        if img_url:
                            print('okk')
                            # If image URL is provided, assume it's unchanged
                            received_img_ids.append(int(img_id))
                        elif img_file:
                            # Image is replaced
                            image = AttributeImage.objects.get(id=img_id, attribute=attr)
                            image.image = img_file
                            image.title = img_title
                            image.type = img_type
                            image.save()
                            received_img_ids.append(image.id)
                    elif img_file:
                        # New image
                        image = AttributeImage.objects.create(
                            attribute=attr,
                            title=img_title,
                            type=img_type,
                            image=img_file
                        )
                        received_img_ids.append(image.id)

                    j += 1

                # Delete images removed on the frontend
                attr.images.exclude(id__in=received_img_ids).delete()
                i += 1

            # Delete attributes removed on the frontend
            condition.attributes.exclude(id__in=received_attr_ids).delete()

            return Response({'status': True, 'message': 'Condition updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': False, 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_200_OK)



class ForumPostListCreateView(APIView):
    permission_classes = [AllowAny]
    def get_queryset(self):
        return ForumPost.objects.all().order_by('-created_at')
        
    def get(self, request):
        posts = ForumPost.objects.all().order_by('-created_at')
        serializer = ForumPostSerializer(posts, many=True)
        return custom_response(data=serializer.data, message="Posts retrieved successfully.")

    def post(self, request):
        name = request.data.get('name')
        content = request.data.get('content')
        department_id = request.data.get('department')
        condition_id = request.data.get('condition')

        post = ForumPost.objects.create(
            user=request.user if request.user.is_authenticated else None,
            username=name if not request.user.is_authenticated else None,
            content=content,
            department_id=department_id,
            condition_id=condition_id
        )
        serializer = ForumPostSerializer(post)
        return custom_response(data=serializer.data, message='Post created successfully.')


class CommentCreateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, post_id):
        post = get_object_or_404(ForumPost, id=post_id)
        name = request.data.get('name')
        content = request.data.get('content')

        comment = Comment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            username=name if not request.user.is_authenticated else None,
            post=post,
            content=content
        )
        serializer = CommentSerializer(comment)
        return custom_response(data=serializer.data, message='Comment added.')


class LikeToggleView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, post_id):
        post = get_object_or_404(ForumPost, id=post_id)
        name = request.data.get('name')

        if request.user.is_authenticated:
            like, created = Like.objects.get_or_create(user=request.user, post=post)
        else:
            like, created = Like.objects.get_or_create(user=None, username=name, post=post)

        if not created:
            like.delete()
            return custom_response(message='Like removed.')
        else:
            return custom_response(message='Post liked.')



class SymptomListView(ListAPIView):
    queryset = Symptoms.objects.all()
    serializer_class = SymptomSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response = {
            'status': True,
            'message': 'Symptoms fetched successfully',
            'data': serializer.data
        }

        return Response(response, status=status.HTTP_200_OK)

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
    permission_classes = (IsAuthenticated,)

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
            