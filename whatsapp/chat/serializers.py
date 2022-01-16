from rest_framework import serializers
from .models import User, Room, Messages

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'dp', 'name', 'contact']

    def update(self, instance, validated_data):
        try:
            dp = validated_data['dp']
            instance.dp = dp
        except:
            pass
        try:
            name = validated_data['name']
            instance.name = name
        except:
            pass

        instance.save()
            
        return instance


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

    def update(self, instance, validated_data):
        print('vd', validated_data)
        try:
            instance.dp = validated_data['dp']
        except:
            pass
        
        try:
            instance.admin = validated_data['admin']
        except:
            pass

        try:
            instance.room = validated_data['room']
        except:
            pass

        try:
            instance.user.add(*validated_data['user'])
        except:
            pass

        instance.save()

        return instance

    
class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"