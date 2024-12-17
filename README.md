# SoftDesk Support API

## Description


SoftDesk Support est une API backend robuste conçue pour offrir une solution complète de gestion de projets et de résolution de problèmes techniques. 
Elle permet aux équipes de collaborer efficacement en suivant et en gérant des projets, des problèmes techniques et leurs résolutions, avec un système de permissions granulaire et sécurisé via JWT (Json Web Token).

## Fonctionnalités principales

- **Gestion des utilisateurs (users)** : Création, modification, suppression et récupération des utilisateurs. Les utilisateurs peuvent choisir leurs préférences de confidentialité.
- **Gestion des projets (projects)** : Les utilisateurs peuvent créer des projets, et seuls les contributeurs de ces projets peuvent y accéder.
- **Gestion des problèmes (Issues)** : Les contributeurs peuvent créer et gérer des problèmes liés à un projet, en assignant des utilisateurs, des priorités et des statuts.
- **Gestion des assignés** : Les assignés ont été désignés par l'auteur d'une issue. Ils peuvent donc voir cette issue mais aussi la modifier, la supprimer et y ajouter des commentaires.
- **Commentaires (comments)** : Les contributeurs et assignés peuvent ajouter des commentaires pour chaque problème.
- **Authentification et autorisation** : L'API utilise des JSON Web Tokens (JWT) pour sécuriser les accès et gérer les permissions des utilisateurs.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Python 3.8 ou plus
- Pip (gestionnaire de paquets Python)
- Django 3.2 ou plus
- Django REST Framework

## Installation

### 1. Clonez le projet

```bash
git clone https://github.com/Kudzu86/P10.git
cd P10
```

### 2. Créez un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
```

### 3. Installez les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquez les migrations

```bash
python manage.py migrate
```

### 5. Créez un superutilisateur (admin)

Pour créer un utilisateur admin (superutilisateur) afin de pouvoir accéder à l'interface d'administration Django, utilisez la commande suivante :

```bash
python manage.py createsuperuser
```

Saisissez les informations demandées.

Identifiants admin de test :
- **Email** : ericauer86@gmail.com
- **Mot de passe** : admin

### 6. Lancez le serveur

```bash
python manage.py runserver
```

L'API sera disponible à l'adresse http://127.0.0.1:8000/.

## Authentification et Utilisation des Tokens

### 1. Authentification (JWT)

Pour obtenir un token JWT, envoyez une requête POST à l'URL suivante avec les informations de l'utilisateur :

**URL :** `POST /api/token/` ce qui correspond à une méthode `POST` à l'url `http://127.0.0.1:8000/api/token/`

**Exemple de requête :**
```json
{
  "email": "ericauer86@gmail.com",
  "password": "admin"
}
```

**Exemple de réponse :**
```json
{
  "access": "votre_token_d'accès",
  "refresh": "votre_token_de_refresh"
}
```
Les tokens d'accès JWT sont généralement valides pour une courte durée (5 à 15 minutes). Le token de refresh permet d'obtenir un nouveau token d'accès sans avoir à se reconnecter. 
Il est recommandé de gérer le renouvellement automatique des tokens côté client pour maintenir une expérience utilisateur fluide :

**URL :** `POST /api/token/refresh/`, il faudra alors utiliser le code `refresh` à la place du code `access` dans le Bearer (voir ci-dessous).

### 2. Utiliser le Bearer Token

Vous pouvez utiliser Postman ou un autre client HTTP pour tester les points de terminaison.
Incluez le token d'accès (récupéré dans la réponse 'access' de la requête d'identification) dans l'en-tête `Headers` des requêtes :

**Format de l'en-tête :**
```http
Authorization: Bearer votre_token_d'accès
```

**Exemple concret :**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Points importants à noter :
* Le mot-clé `Bearer` est **obligatoire**
* Le token suit immédiatement après `Bearer`, séparé par un espace
* Chaque requête nécessitant une authentification doit inclure cet en-tête

## Utilisation de l'API

L'API permet de gérer plusieurs ressources, telles que les utilisateurs, les projets, les issues, et les commentaires.

### Exemples de points de terminaison

#### Créer un utilisateur

**URL :** `POST /users/users/`

Exemple de requête :
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Créer un projet

**URL :** `POST /projects/projects/`

Exemple de requête :
```json
{
  "title": "Nouveau Projet",
  "description": "Un projet test"
}
```

#### Créer un problème (issue)

**URL :** `POST /issues/projects/project_id/issues/`

Exemple de requête :
```json
{
  "title": "Problème de connexion",
  "description": "L'utilisateur ne peut pas se connecter à l'application."
}
```

#### Créer un commentaire

**URL :** `POST /comments/projects/project_id/issues/issues_id/comments/`

Exemple de requête :
```json
{
    "content": "Ce commentaire est très détaillé et dépasse les 10 caractères !"
}
```

Après avoir créé un commentaire (par exemple à l'URL `http://127.0.0.1:8000/comments/projects/42/issues/27/comments/`), vous recevrez une réponse avec l'ID du commentaire. 

Exemple de réponse :
```json
{
    "id": 16,
    "content": "Ce commentaire est très détaillé et dépasse les 10 caractères !",
    "created_at": "2024-12-17T15:45:31.477509Z",
    "author": 15,
    "issue": 27,
    "project": 42
}
```

### Opérations CRUD détaillées

Après la création d'une ressource (commentaire, projet, issue), vous disposez de plusieurs options de manipulation puissantes.
Vous pouvez effectuer les actions suivantes en ajoutant l'identifiant à l'URL :

- **GET** : Consulter les détails d'une ressource spécifique
  - Exemple : `http://127.0.0.1:8000/comments/projects/42/issues/27/comments/16/`
  - Permet de récupérer toutes les informations du commentaire

- **PATCH** : Mettre à jour partiellement une ressource
  - Modification ciblée sans remplacer l'intégralité des données
  - Utile pour des mises à jour rapides et précises

- **DELETE** : Supprimer définitivement une ressource
  - Suppression complète et irréversible de l'élément
  - Nécessite les permissions appropriées


  
## Sécurité

Cette application utilise des **JSON Web Tokens (JWT)** pour authentifier et autoriser les utilisateurs.

## Auteur

**Eric Auer**
- GitHub : [@Kudzu86](https://github.com/Kudzu86/P10)
- Email : ericauer86@gmail.com

## Licence

Ce projet est sous **licence MIT**. Voir le fichier *LICENSE* pour plus de détails.
