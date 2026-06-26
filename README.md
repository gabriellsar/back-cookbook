# 🍲 Panela — Backend (API)

API REST do **Panela**, uma plataforma de receitas colaborativas com suporte a *fork*
(derivação de receitas entre usuários, no estilo do GitHub). Este repositório contém
**apenas o backend**; a interface web está em `front-cookbook`.

> **Disciplina:** Programação para Web — PUC-Rio — 2026/1
> **Trabalho 2** — Aluno: **Gabriel Rosas**

---

## 📖 Descrição do projeto

O **Panela** é um "livro de receitas" comunitário. Cada usuário pode publicar receitas,
e qualquer outro usuário pode **dar fork** numa receita existente para criar a sua própria
versão adaptada — mantendo o vínculo com a receita original (formando uma árvore de
derivações). Usuários do tipo **Guardião** podem ainda "trancar" ingredientes e passos como
*segredos de família*, que não podem ser alterados por quem deriva a receita.

Este backend expõe uma **API REST** (Django REST Framework) com autenticação **JWT**,
responsável por toda a persistência e regras de negócio:

- Cadastro e autenticação de usuários (JWT com *refresh token*).
- CRUD de receitas, ingredientes e passos.
- **Fork** de receitas (clonagem com vínculo à original).
- **Avaliações** (1 a 5 estrelas) com cálculo de média.
- Campos de **tempo de preparo**, **porções** e **link de vídeo**.
- Documentação interativa automática (Swagger / Redoc).

---

## 🧱 Stack e tecnologias

| Recurso | Tecnologia |
|---|---|
| Linguagem | Python 3.14 |
| Framework web | Django 6.0 |
| API REST | Django REST Framework |
| Autenticação | djangorestframework-simplejwt (JWT) |
| Documentação | drf-spectacular (OpenAPI 3 / Swagger / Redoc) |
| CORS | django-cors-headers |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL (via `dj-database-url`) |
| Deploy | Gunicorn (ex.: Render) |

---

## 📂 Estrutura do projeto

```
back-cookbook/
├── core/                  # Configuração do projeto Django
│   ├── settings.py        # Settings (DRF, JWT, CORS, banco)
│   └── urls.py            # Rotas raiz + auth + Swagger/Redoc
├── app/                   # Camada de aplicação (API)
│   ├── serializers.py     # Serializers (Recipe, Ingredient, Step, User)
│   ├── urls.py            # Router DRF (/recipes, /ingredients, /steps)
│   └── views/
│       ├── RecipeViewSet.py       # CRUD + ações fork e rate
│       ├── IngredientViewSet.py
│       ├── StepViewSet.py
│       └── AuthViewSet.py         # Registro de usuário
├── infra/                 # Camada de domínio (modelos)
│   ├── models/
│   │   ├── Recipe.py
│   │   ├── Ingredient.py
│   │   ├── Step.py
│   │   ├── Rating.py
│   │   ├── User.py                # CustomUser (Guardião/Herdeiro)
│   │   └── _LockableRecipeComponent.py
│   └── migrations/
├── manage.py
├── requirements.txt
└── build.sh               # Script de build para deploy
```

---

## 🚀 Como rodar localmente

### 1. Pré-requisitos
- Python 3.12+ (testado em 3.14)

### 2. Ambiente virtual e dependências

```bash
cd back-cookbook
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Migrações do banco

```bash
python manage.py migrate
```

### 4. (Opcional) Criar um superusuário para o admin

```bash
python manage.py createsuperuser
```

### 5. Subir o servidor

```bash
python manage.py runserver
```

A API ficará disponível em **http://localhost:8000**.

> O frontend espera o backend em `http://localhost:8000` por padrão.

---

## 📚 Documentação da API

Com o servidor rodando:

- **Swagger UI:** http://localhost:8000/api/docs/swagger/
- **Redoc:** http://localhost:8000/api/docs/redoc/
- **Schema OpenAPI (JSON):** http://localhost:8000/api/schema/

---

## 🔌 Principais endpoints

### Autenticação

| Método | Rota | Auth | Descrição |
|---|---|:---:|---|
| `POST` | `/api/auth/register/` | ❌ | Cadastra usuário (`username`, `email`, `password`) |
| `POST` | `/api/auth/login/` | ❌ | Retorna `access` e `refresh` (JWT) |
| `POST` | `/api/auth/refresh/` | ❌ | Renova o `access` token |

### Receitas

| Método | Rota | Auth | Descrição |
|---|---|:---:|---|
| `GET` | `/api/recipes/` | ❌ | Lista receitas (mais recentes primeiro) |
| `POST` | `/api/recipes/` | ✅ | Cria receita |
| `GET` | `/api/recipes/{id}/` | ❌ | Detalha receita |
| `PATCH` | `/api/recipes/{id}/` | ✅ | Atualiza parcialmente |
| `DELETE` | `/api/recipes/{id}/` | ✅ | Remove receita |
| `POST` | `/api/recipes/{id}/fork/` | ✅ | Clona a receita para o usuário atual |
| `POST` | `/api/recipes/{id}/rate/` | ✅ | Avalia (`value` de 1 a 5) — *upsert* |

### Ingredientes e Passos

| Método | Rota | Auth | Descrição |
|---|---|:---:|---|
| `GET/POST` | `/api/ingredients/` | ✅ p/ escrita | CRUD de ingredientes |
| `GET/POST` | `/api/steps/` | ✅ p/ escrita | CRUD de passos |

> Autenticação via header `Authorization: Bearer <access_token>`.

---

## 🧬 Modelo de dados (resumo)

- **CustomUser** — usuário com `role` (`GUARDIAN` ou `HEIR`).
- **Recipe** — `title`, `description`, `prep_time` (min), `servings`, `video_url`,
  `tags` (lista de categorias), `forked_from` (auto-referência), `affectionate_note`,
  `created_at`.
- **Ingredient** / **Step** — pertencem a uma `Recipe` e possuem `is_locked`
  (segredo de família, herdado em forks).
- **Rating** — `recipe` + `user` + `value` (1–5), com `unique_together(recipe, user)`
  (cada usuário avalia uma receita só uma vez; reavaliar atualiza a nota).

O `RecipeSerializer` ainda calcula dinamicamente: `average_rating`, `rating_count`,
`forks_count` e `my_rating` (a nota do usuário autenticado).

---

## ✅ O que foi testado e **funcionou**

Testes realizados via `curl` ponta a ponta contra o servidor de desenvolvimento e via
`manage.py shell`:

- ✅ **Cadastro** de usuário (`POST /api/auth/register/` → `201`).
- ✅ **Login JWT** (`POST /api/auth/login/`) retornando `access`/`refresh`.
- ✅ **Criação de receita** com `prep_time` e `servings`.
- ✅ **Avaliação** (`POST /api/recipes/{id}/rate/`): cálculo correto da média e
  comportamento de *upsert* verificado (duas notas do mesmo usuário não duplicam —
  a média recalcula corretamente, ex.: notas 5 e 4 → média 3.5 após o usuário trocar
  a própria nota de 5 para 3).
- ✅ **Validação de nota inválida** (`value: 9` → `400 Bad Request`).
- ✅ **Exclusão** de receita (`DELETE` → `204`).
- ✅ Campos calculados do serializer (`average_rating`, `rating_count`, `forks_count`,
  `my_rating`) retornando valores corretos.
- ✅ **`role` no token JWT:** o login (`CustomTokenObtainPairView`) agora inclui o papel
  (`role`) e o `username` no *payload* do JWT — verificado decodificando o token.
- ✅ **Segredo de família (lock) — regra de proteção:** validado ponta a ponta que o
  **autor** de uma receita **original** consegue editar seus próprios itens trancados
  (`200`), enquanto quem faz **fork** **não** consegue alterar o segredo herdado (`403`).
- ✅ **Tags** persistidas no backend (campo `tags` em `Recipe`) e retornadas na listagem.
- ✅ `python manage.py check` sem nenhum problema.
- ✅ Migrações aplicadas com sucesso (`infra/0001`, `infra/0002` e `infra/0003`).

## ⚠️ O que **não funcionou / limitações conhecidas**

- ⚠️ **Sem endpoint de troca de senha** e **sem recuperação de senha** ("esqueci minha
  senha"): não foram implementados no backend.
- ⚠️ **Atribuição de papel (Guardião/Herdeiro):** todo usuário é criado como **Herdeiro**
  (`HEIR`) e **não há tela para virar Guardião**. Isso não impede o uso dos "segredos de
  família": a proteção do backend é baseada em **autoria + fork** (qualquer autor tranca os
  itens da própria receita original; forks respeitam o cadeado), e não no papel global.
- ℹ️ **Upload de foto:** removido do escopo (MVP). As receitas usam ícones no frontend.
- ℹ️ **Persistência de mídia em produção:** o deploy gratuito (Render) não persiste
  arquivos enviados — outro motivo para a foto ter ficado fora do MVP.

> Conforme a orientação do enunciado, as limitações acima estão **explicitamente
> relatadas** aqui.

---

## 👤 Autor

**Gabriel Rosas** — PUC-Rio, Programação para Web 2026/1.
