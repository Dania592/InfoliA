from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserSerializer, LoginSerializer

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Utilisateur enregistré"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        return Response({
            "message": "Connexion réussie !",
            "pseudo": user.pseudo,
            "is_admin": user.is_admin
        }, status=status.HTTP_200_OK)
    return Response({"detail": "Identifiants invalides"}, status=status.HTTP_400_BAD_REQUEST)
