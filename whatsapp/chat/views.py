from django.http.request import QueryDict
from rest_framework.views import APIView
from chat.serializers import RoomSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from .models import Otp, Room, User

from knox.models import AuthToken

from sms import send_sms

import random
import json


def otp():
    return random.randint(100000, 999999)


class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            code = otp()
            send_sms(
                f'Here is the OTP: {code}',
                '+12813774813',
                request.data['contact'],
                fail_silently=False
            )

            user = serializer.save()
            Otp.objects.create(user=user, otp=code)

        except:
            return Response({
                'invalid_number': 'Seems you provided an invalid number. Please check it again and don\'t forget to include the country code.'
            }, status.HTTP_406_NOT_ACCEPTABLE)

        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data
        })

    def put(self, request):
        try:
            user = User.objects.get(contact=request.data['contact'])
        except:
            return Response({
                'invalid_number': 'Please provide a valid number'
            }, status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.get_serializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        try:
            code = otp()
            send_sms(
                f'Here is the OTP: {code}',
                '+12813774813',
                request.data['contact'],
                fail_silently=False
            )

            contact = serializer.save()

            try:
                Otp.objects.get(user=user).delete()
            except:
                pass

            Otp.objects.create(user=contact, otp=code)

        except:
            return Response({
                'invalid_number': 'Seems you provided an invalid number. Please check it again and don\'t forget to include the country code.'
            }, status.HTTP_406_NOT_ACCEPTABLE)

        return Response({
            'user': UserSerializer(contact, context=self.get_serializer_context()).data
        })


class ValidateOtp(APIView):
    def put(self, request):
        code = otp()
        try:
            Otp.objects.filter(user=User.objects.get(
                contact=request.data['contact'])).delete()
        except:
            pass

        try:
            send_sms(
                f"Here is the OTP: {code}",
                "+12813774813",
                request.data['contact'],
                fail_silently=False
            )
            Otp.objects.create(user=User.objects.get(
                contact=request.data['contact']), otp=code)
        except:
            return Response({
                'invalid_number': 'There is some problem.Please check the number and try again.'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response({
            'message': 'OTP sent!'
        })

    def post(self, request):
        try:
            code = request.data['otp']
        except:
            return Response({
                "invalid_otp": "Please Enter the OTP send to your number."
            }, status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(contact=request.data['contact'])
            db_code = Otp.objects.get(user=user).otp
        except:
            return Response({
                'invalid_otp': "There is either no OTP registered on this number or the number is not registered."
            }, status.HTTP_400_BAD_REQUEST)

        if int(code) == db_code:
            Otp.objects.filter(user=user).delete()
            _, token = AuthToken.objects.create(user)

            return Response({
                'token': token
            })

        Otp.objects.filter(user=User.objects.get(
            contact=request.data['contact'])).delete()

        return Response({
            'invalid_otp': 'Incorrect OTP provided! Now Please click on the RESEND button to get a new OTP as older one has been expired because of wrong attempt!'
        }, status.HTTP_400_BAD_REQUEST)


class CreateRoomView(generics.GenericAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        serializer = self.get_serializer(
            self.get_queryset().filter(user=request.user), many=True)
        [room.update({'admin': UserSerializer(User.objects.get(id=room['admin']
                                                               ), context=self.get_serializer_context()).data, 'user': [UserSerializer(User.objects.get(id=i), context=self.get_serializer_context()).data for i in room['user']]}) for room in serializer.data]

        return Response(serializer.data)

    def post(self, request):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        print(request.data)
        try:
            request.data['admin'] = User.objects.get(
                contact=request.data['admin']).id
            request.data['user'] = User.objects.get(
                contact=request.data['user']).id
        except:
            return Response({
                'error': 'there is some error. Please try again!'
            }, status.HTTP_400_BAD_REQUEST)

        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = serializer.save()

        room_details = RoomSerializer(
            room, context=self.get_serializer_context()).data
        room_details.update({'admin': UserSerializer(User.objects.get(id=room_details['admin']), context=self.get_serializer_context()).data, 'user': [
                            UserSerializer(User.objects.get(id=i), context=self.get_serializer_context()).data for i in room_details['user']]})

        return Response(room_details)

    def put(self, request):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        try:
            room = Room.objects.get(id=request.data['room_id'])
        except:
            return Response({
                'room_not_exist': "No such room created. Please create a room to add users"
            }, status.HTTP_404_NOT_FOUND)

        if room.admin == request.user:
            try:
                request.data['admin'] = User.objects.get(
                    contact=request.data['admin']).id
            except:
                pass

            print(request.data)
            try:
                users = [User.objects.get(
                    contact=con).id for con in json.loads(request.data['user'])]

                del request.data['user']

                [request.data.update({'user': u}) for u in users]
            except:
                pass

            print(request.data)
            serializer = self.get_serializer(
                room, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)

            updated_room = serializer.save()

            room_details = RoomSerializer(
                updated_room, context=self.get_serializer_context()).data
            room_details.update({'admin': UserSerializer(User.objects.get(id=room_details['admin']), context=self.get_serializer_context()).data, 'user': [
                                UserSerializer(User.objects.get(id=i), context=self.get_serializer_context()).data for i in room_details['user']]})

            return Response(room_details)

        return Response({
            'not_allowed': 'You are not allowed to perform this action.'
        }, status.HTTP_403_FORBIDDEN)

        
        