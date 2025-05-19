from rest_framework import serializers
from django.db.models import Q
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'names',  'is_active', 'is_staff', 'is_admin', 'roles')
        

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['roles'] is not None:
            roles = []
            for role in data['roles']:
                obj = RoleSerializer(
                Role.objects.get(pk=role)).data
                roles.append(obj)
            data['roles']=roles
        return data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Condition
        fields = '__all__'

class AttributeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeImage
        fields = ['id', 'title', 'type', 'image']


class AttributeSerializer(serializers.ModelSerializer):
    images = AttributeImageSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ['id', 'title', 'content', 'images']

class AttributeSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'title', 'content']

class ConditionSerializer2(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)  # uses related_name='attributes'

    class Meta:
        model = Condition
        fields = ['id', 'name', 'department', 'attributes']

class ConditionSerializer3(serializers.ModelSerializer):
    first_attribute = serializers.SerializerMethodField()

    class Meta:
        model = Condition
        fields = '__all__'  # Alternatively: list fields explicitly if you want to control order

    def get_first_attribute(self, obj):
        first_attr = obj.attributes.first()  # uses related_name='attributes'
        if first_attr:
            return AttributeSerializer2(first_attr).data
        return None

class ConditionSerializer4(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Condition
        fields = '__all__'

    def get_attributes(self, obj):
        considered_symptom_ids = self.context.get('considered_symptom_ids', [])

        if not considered_symptom_ids:
            return []

        # Get symptom names from IDs
        symptom_names = Symptoms.objects.filter(id__in=considered_symptom_ids).values_list('name', flat=True)

        # Build a Q object to search for any symptom name in the content
        query = Q()
        for name in symptom_names:
            query |= Q(content__icontains=name)

        # Filter the condition's attributes based on symptom name matches
        attributes = obj.attributes.filter(query).distinct()
        return AttributeSerializer2(attributes, many=True).data

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptoms
        fields = '__all__'

class SymptomSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Symptoms
        fields = ('id', 'name', 'conditions', 'further_management', 'referral_criteria')
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['conditions'] is not None:
            conditions = []
            for condition in data['conditions']:
                obj = ConditionSerializer(
                Condition.objects.get(pk=condition)).data
                conditions.append(obj)
            data['conditions']=conditions
        return data

class CommentSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_display', 'content', 'created_at']

    def get_user_display(self, obj):
        return obj.user.email if obj.user else obj.username


class ForumPostSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    department = DepartmentSerializer(read_only=True)
    condition = ConditionSerializer(read_only=True)

    class Meta:
        model = ForumPost
        fields = ['id', 'user_display', 'department', 'condition', 'content', 'created_at', 'comments', 'likes_count']

    def get_user_display(self, obj):
        return obj.user.email if obj.user else obj.username

    def get_likes_count(self, obj):
        return obj.likes.count()


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    user_id = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)