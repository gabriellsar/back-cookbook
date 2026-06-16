from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from infra.models import CustomUser, Recipe, Ingredient, Step

class RecipeAPITests(APITestCase):
    def setUp(self):
        # 1. Usuários
        self.guardian = CustomUser.objects.create_user(username='guardian', password='123', role=CustomUser.Role.GUARDIAN)
        self.heir = CustomUser.objects.create_user(username='heir', password='123', role=CustomUser.Role.HEIR)

        # 2. Receita Raiz (do Guardião)
        self.root_recipe = Recipe.objects.create(author=self.guardian, title='Bolo de Fubá', description='Clássico')
        
        # 3. Componentes
        self.ing = Ingredient.objects.create(recipe=self.root_recipe, name='Fubá', quantity='2 xícaras', is_locked=True)
        self.step = Step.objects.create(recipe=self.root_recipe, order=1, instruction='Misture tudo', is_locked=True)

        self.list_url = reverse('recipe-list')
        self.detail_url = reverse('recipe-detail', kwargs={'pk': self.root_recipe.id})
        self.fork_url = reverse('recipe-fork', kwargs={'pk': self.root_recipe.id})

    def test_list_recipes_unauthenticated(self):
        """Qualquer usuário (mesmo deslogado) deve conseguir listar as receitas (IsAuthenticatedOrReadOnly)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_recipe_authenticated(self):
        """Apenas usuários logados podem criar uma receita do zero"""
        self.client.force_authenticate(user=self.guardian)
        data = {'title': 'Torta Salgada', 'description': 'Torta rápida'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)

    def test_fork_recipe_success(self):
        """O Fork deve copiar a receita, ingredientes e passos corretamente"""
        self.client.force_authenticate(user=self.heir)
        data = {'affectionate_note': 'Para lembrar de casa'}
        response = self.client.post(self.fork_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica no banco de dados se a cópia profunda ocorreu
        new_recipe = Recipe.objects.get(id=response.data['id'])
        self.assertEqual(new_recipe.author, self.heir)
        self.assertEqual(new_recipe.forked_from, self.root_recipe)
        
        # Verifica se os ingredientes e passos foram clonados
        self.assertEqual(new_recipe.ingredients.count(), 1)
        self.assertEqual(new_recipe.steps.count(), 1)
        
        # O clone deve herdar a propriedade 'is_locked'
        self.assertTrue(new_recipe.ingredients.first().is_locked)