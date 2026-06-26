from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Avg
from infra.models import Recipe, Ingredient, Step
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer de login que adiciona o papel (role) e o username ao
    payload do JWT, permitindo que o frontend identifique Guardião/Herdeiro.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

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
    
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), write_only=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'recipe', 'name', 'quantity', 'is_locked']


class StepSerializer(serializers.ModelSerializer):
    """
    Serializador para a entidade Step.
    """
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), write_only=True)

    class Meta:
        model = Step
        fields = ['id', 'recipe', 'step_number', 'instruction', 'is_locked']


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializador principal da entidade Recipe.
    """

    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True, read_only=True)

    author_name = serializers.ReadOnlyField(source='author.username')
    forked_from_title = serializers.ReadOnlyField(source='forked_from.title')

    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    forks_count = serializers.SerializerMethodField()
    my_rating = serializers.SerializerMethodField()

    tags = serializers.ListField(
        child=serializers.CharField(max_length=40),
        required=False,
    )

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
            'prep_time',
            'servings',
            'video_url',
            'tags',
            'average_rating',
            'rating_count',
            'forks_count',
            'my_rating',
            'ingredients',
            'steps'
        ]
        read_only_fields = ['author', 'created_at']

    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(avg=Avg('value'))['avg']
        return round(avg, 1) if avg is not None else 0

    def get_rating_count(self, obj):
        return obj.ratings.count()

    def get_forks_count(self, obj):
        return obj.forks.count()

    def get_my_rating(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        rating = obj.ratings.filter(user=request.user).first()
        return rating.value if rating else None