from rest_framework import serializers
from .models import CustomUser, Organisation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

class RegistrationSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(max_length=50, required=True)
    lastName = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(validators=[validate_email])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ('userId', 'firstName', 'lastName', 'email', 'password', 'phone')
    

    def validate(self, data):
        errors = {}
        if not data.get('firstName'):
            errors['firstName'] = 'First name is required'
        if not data.get('lastName'):
            errors['lastName'] = 'Last name is required'
        if not data.get('email'):
            errors['email'] = 'Email is required'
        if not data.get('password'):
            errors['password'] = 'Password is required'
        if CustomUser.objects.filter(email=data.get('email')).exists():
            errors['email'] = 'User with this email has been created'
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = CustomUser(
                email=validated_data['email'],
                username=validated_data['email'],  # Set username to email
                firstName=validated_data['firstName'],
                lastName=validated_data['lastName'],
                phone=validated_data.get('phone', '')  # Default to empty string if phone is not provided
            )
            user.set_password(validated_data['password'])
            user.save()

            organisation = Organisation.objects.create(
                name=f"{validated_data['firstName']}'s Organisation"
            )
            organisation.users.add(user)
        return user

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ("orgId", "name", "description", )
