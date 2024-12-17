from rest_framework import serializers
from datetime import datetime
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()  # La date d'inscription est en lecture seule.

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'birthdate', 'password', 'can_be_contacted', 'can_data_be_shared')
        extra_kwargs = {
            'password': {'write_only': True}  # Le mot de passe est en écriture seule.
        }
        
    def validate_birthdate(self, value):
        """
        Valider que l'utilisateur a au moins 15 ans.
        """
        today = datetime.today().date()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 15:
            raise serializers.ValidationError("Vous devez avoir au moins 15 ans pour vous inscrire.")
        return value

    def create(self, validated_data):
        """
        Crée un utilisateur en hachant son mot de passe.
        """
        consent = validated_data.get('consent', False)

        user = User.objects.create_user(**validated_data)
        return user
