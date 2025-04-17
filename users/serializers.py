from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email',  'is_active', 'is_staff', 'is_admin', 'roles')
        

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
    class Meta:
        model = Condition
        fields = '__all__'

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'title', 'content']

class ConditionSerializer2(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)  # uses related_name='attributes'

    class Meta:
        model = Condition
        fields = ['id', 'name', 'department', 'attributes']

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
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class ForumPostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ['id', 'user', 'content', 'created_at', 'comments', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

class ChangePasswordSerializer(serializers.Serializer):
    model = User
    user_id = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)