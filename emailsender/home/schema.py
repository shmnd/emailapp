from rest_framework import serializers
from home.models import Customers

class EnquiryDetailsSchema(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = '__all__'

    def to_representation(self,instance):
        data = super().to_representation(instance)
        for key in data.keys():
            try:
                if data[key] is None:
                    data[key] = " "
            except KeyError:
                pass
        return data