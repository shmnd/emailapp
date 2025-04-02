from rest_framework import serializers
from home.models import Customers
import re
from home.models import Subscriber

class CreateEnquiresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = '__all__'

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')

        if email and not email.endswith('.com'):
            raise serializers.ValidationError({"email": "Email must end with '.com'"})

        # Validate the Indian phone number:
        # - Optional '+91' country code (can include a hyphen or space)
        # - Must start with digits 6-9
        indian_phone_regex = re.compile(r'^(\+91[-\s]?)?[6-9]\d{9}$')
        if phone and not indian_phone_regex.match(phone):
            raise serializers.ValidationError({"phone": "Enter a valid Indian phone number."})
        return super().validate(attrs)
    

    def create(self, validated_data):
        instance = Customers(
            name = validated_data.get('name'),
            email = validated_data.get('email'),
            phone = validated_data.get('phone')
        )
        instance.save()
        return instance
    