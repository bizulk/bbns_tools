# En bref

Ce script permet d'envoyer les photos des animations aux parents 
Les mails et fichier de photos sont dans un fichier excel (ods ou xlsx) : 
- une colonne contient les numéro de photos séparés par une virgule
- une colonne contient les mails des parents

Le script contient une zone de paramètres pour localiser le fichier, définir les colonnes à utiliser, et une fonction pour construire le nom du fichier.

On utilise un compte gmail pour les envois (credentials à récuperer et token à générer)

# Infos techniques

## Installer et Utiliser l'API Python de Google pour Gmail : 
 - HOWTO  ouvrir une session avec l'API [ici](https://developers.google.com/gmail/api/quickstart/python). Il faut télécharger les credentials.
 - HOWTO envoyer un mail [ici](https://developers.google.com/gmail/api/guides/sending)

## BUG rencontrés et corrigés
	- fixed : lecture d'un fichier dox ou odt (par test extension)
	- fixed : problème dans l'appel encodage base 64 qui ont conduit à d'autres erreurs de traitement : correction [ici](https://stackoverflow.com/questions/38633781/python-gmail-api-not-json-serializable/39693258#39693258)
	- fixed : L'autorisation d'envoyer des mails : modification du SCOPE.
	- non fixed - à la création du token c'est toujours le projet 'quickstart' identifié
	
La [doc](https://developers.google.com/gmail/api/auth/scopes) Getting Started de l'API 

