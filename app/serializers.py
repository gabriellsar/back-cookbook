from rest_framework import serializers
from infra.models import Recipe, Ingredient, Step
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializador para o registo de novos utilizadores.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializador para a entidade Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'is_locked']


class StepSerializer(serializers.ModelSerializer):
    """
    Serializador para a entidade Step.
    """
    class Meta:
        model = Step
        fields = ['id', 'step_number', 'instruction', 'is_locked']


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializador principal da entidade Recipe.
    """

    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True, read_only=True)
    
    author_name = serializers.ReadOnlyField(source='author.username')
    forked_from_title = serializers.ReadOnlyField(source='forked_from.title')

    class Meta:
        model = Recipe
        fields = [
            'id', 
            'title', 
            'description', 
            'author', 
            'author_name',           
            'created_at', 
            'forked_from', 
            'forked_from_title',     
            'affectionate_note', 
            'ingredients',           
            'steps'                  
        ]
        read_only_fields = ['author', 'created_at']