# Activité publique et spectateurs

Le menu affiche les parties en ligne lancées avec au moins un humain connecté et les résultats des parties terminées depuis l’activation de cette fonctionnalité. Les parties locales ne sont pas transmises au serveur.

Le spectateur possède une connexion séparée, sans siège joueur. Le serveur refuse les événements de jeu sur cette connexion. Une liste explicite de champs publics est transmise : plateau, scores calculés par le moteur legacy, compte des cartes, cartes publiques, bataille, Oracle public et événements publics. Les mains, informations d’espionnage, ordre de pioche, jetons de reconnexion et journal privé ne sont jamais inclus. Aucun moteur de jeu ni bot ne tourne dans la vue spectateur.

Les clients joueurs doivent actualiser leur page pour transmettre les scores et puissances de bataille publics. Pour un ancien client, ces valeurs restent en attente : le serveur ne réimplémente pas les règles.

## Historique et Render

### Solution gratuite : Render Free + Neon Free

Le serveur accepte une base PostgreSQL externe. Neon Free convient pour ces petits résumés ; rester sur le plan Free et surveiller ses quotas. Aucun disque Render payant n’est nécessaire dans cette configuration.

1. Créer un compte sur https://console.neon.tech/signup et un projet `TRIBU` sur le plan **Free**. Choisir si possible une région proche du service Render.
2. Dans Neon, ouvrir **Connect** et copier la chaîne de connexion PostgreSQL. Garder le paramètre TLS fourni (`sslmode=require`, ou `verify-full`).
3. Dans Render, ouvrir le service TRIBU puis **Environment**. Ajouter la variable **TRIBU_HISTORY_DATABASE_URL** et coller la chaîne comme valeur. Cette valeur est un secret : ne pas la mettre dans GitHub, dans le navigateur du jeu, ni dans une conversation.
4. Enregistrer et redéployer. Le serveur crée automatiquement sa seule table, `tribu_public_history`, puis recharge les résultats. Aucun SQL à saisir manuellement.
5. Terminer une partie en ligne de test, vérifier l’historique, puis redémarrer le service Render et vérifier que le résultat reste présent.

Le serveur lit la base au démarrage et écrit lors d’une nouvelle victoire. L’affichage des spectateurs est servi depuis sa mémoire, sans requête SQL à chaque mouvement. Les connexions inactives sont fermées afin de laisser Neon se mettre en veille. Seuls les 500 derniers résumés sont conservés, dont 100 affichés. La partie ne dépend pas de la disponibilité de la base : en cas d’échec, les résultats attendent en mémoire et dans le cache local, avec nouvelle tentative toutes les 60 secondes. Un arrêt de Render avant une sauvegarde distante réussie peut perdre ces résultats en attente.

La reprise des écritures et la fusion après un chargement retardé sont testées localement. La connexion réelle et la conservation après redémarrage Render doivent être vérifiées après ajout de la variable. Aucun compte externe n’est créé et aucune formule payante n’est activée par le code.

Documentation de l’offre : https://neon.com/docs/introduction/plans

### Stockage local (si aucune base externe n’est configurée)

Par défaut, le serveur écrit les 500 derniers résultats dans `server/data/history.json`. L’interface affiche les 100 plus récents. Ce fichier doit être conservé entre les déploiements. Un redémarrage avec le même fichier recharge l’historique ; aucun historique antérieur à l’activation ne peut être reconstruit.

Sur Render, le système de fichiers ordinaire est temporaire. Pour une conservation durable :

1. Vérifier dans le service Render si un disque persistant est déjà présent.
2. Utiliser son point de montage ; par exemple `/var/data`.
3. Définir `TRIBU_HISTORY_FILE=/var/data/tribu/history.json` dans les variables d’environnement du service.
4. Redéployer et vérifier qu’un résultat de test reste disponible après un redémarrage.

Les disques persistants nécessitent un service payant. Ne pas changer d’abonnement automatiquement. Si aucun disque n’existe, décider du stockage avec le propriétaire avant de le créer. Documentation : https://render.com/docs/disks

Les tests locaux valident le rechargement du fichier, mais ne prouvent pas la configuration du service Render. Aucun disque Render n’est créé par ce changement.

## Vérification

Depuis `server`, installer les dépendances puis lancer `npm test`. Les tests couvrent le filtrage des informations, le refus des actions spectateur, l’absence de siège occupé, les mises à jour en direct, les résultats et le redémarrage du serveur.
