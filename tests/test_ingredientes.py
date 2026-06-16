from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from infra.models import CustomUser, Recipe, Ingredient

class IngredientPermissionsTests(APITestCase):
    def setUp(self):
        self.guardian = CustomUser.objects.create_user(username='guardian', password='123', role=CustomUser.Role.GUARDIAN)
        self.heir = CustomUser.objects.create_user(username='heir', password='123', role=CustomUser.Role.HEIR)

        # Receita Raiz do Guardião
        self.root_recipe = Recipe.objects.create(author=self.guardian, title='Root Recipe', description='...')
        self.locked_ing_root = Ingredient.objects.create(recipe=self.root_recipe, name='Segredo', quantity='1g', is_locked=True)
        
        # Receita Derivada (Fork) do Herdeiro
        self.forked_recipe = Recipe.objects.create(author=self.heir, title='Fork Recipe', description='...', forked_from=self.root_recipe)
        
        # Ingrediente Trancado que foi copiado para o Fork
        self.locked_ing_fork = Ingredient.objects.create(recipe=self.forked_recipe, name='Segredo', quantity='1g', is_locked=True)
        # Ingrediente Destrancado no Fork (criado ou copiado aberto)
        self.unlocked_ing_fork = Ingredient.objects.create(recipe=self.forked_recipe, name='Sal', quantity='1 pitada', is_locked=False)

    def test_guardian_can_edit_own_locked_ingredient(self):
        """O Guardião DEVE conseguir editar o próprio ingrediente trancado na Receita Raiz"""
        self.client.force_authenticate(user=self.guardian)
        url = reverse('ingredient-detail', kwargs={'pk': self.locked_ing_root.id})
        response = self.client.patch(url, {'quantity': '2g'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_heir_cannot_edit_locked_ingredient_on_fork(self):
        """O Herdeiro NÃO PODE editar um ingrediente trancado na sua própria receita derivada (Fork)"""
        self.client.force_authenticate(user=self.heir)
        url = reverse('ingredient-detail', kwargs={'pk': self.locked_ing_fork.id})
        response = self.client.patch(url, {'quantity': '2g'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_heir_cannot_delete_locked_ingredient_on_fork(self):
        """O Herdeiro NÃO PODE deletar um ingrediente trancado no Fork"""
        self.client.force_authenticate(user=self.heir)
        url = reverse('ingredient-detail', kwargs={'pk': self.locked_ing_fork.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_heir_can_edit_unlocked_ingredient_on_fork(self):
        """O Herdeiro DEVE conseguir editar um ingrediente que está destrancado no seu Fork"""
        self.client.force_authenticate(user=self.heir)
        url = reverse('ingredient-detail', kwargs={'pk': self.unlocked_ing_fork.id})
        response = self.client.patch(url, {'quantity': '3 pitadas'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)