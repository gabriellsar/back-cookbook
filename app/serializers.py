from rest_framework import serializers
from infra.models import CustomUser, Recipe, Ingredient, Step

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['role']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'is_locked']

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'order', 'instruction', 'is_locked']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True, read_only=True)
    author_name = serializers.ReadOnlyField(source='author.username')
    forked_from_title = serializers.ReadOnlyField(source='forked_from.title')

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'author', 'author_name', 
            'forked_from', 'forked_from_title', 'affectionate_note',
            'ingredients', 'steps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'forked_from']