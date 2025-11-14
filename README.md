📊 Pipeline de Traitement de Données Client avec Segmentation RFM
🎯 Description du Projet
Ce pipeline ETL (Extract, Transform, Load) automatise le traitement des données commerciales et implémente une segmentation RFM (Récence, Fréquence, Montant) pour analyser la valeur et le comportement des clients. Le processus transforme des données brutes Excel en segments clients actionnables, prêts pour l'analyse dans Power BI.

🔄 Architecture du Pipeline
Flux de Données
text
Fichiers Excel → Nettoyage → CSV Intermédiaires → Base MySQL → Calcul RFM → Segments Clients → Rapports → Power BI
📁 Structure des Fichiers
Données d'Entrée (À placer dans le dossier spécifié)
ventes.xlsx - Données des transactions commerciales

clients.xlsx - Informations sur les clients

stock.xlsx - Données d'inventaire et de stock

achats.xlsx - Données des approvisionnements

Sorties Générées
Données nettoyées : Fichiers CSV dans le dossier "Data transformed"

Base de données : Tables MySQL avec métriques RFM

Rapports RFM : Fichiers CSV et synthèses dans "RFM_Results"

⚙️ Installation et Configuration
Prérequis
Python 3.7+

MySQL Server

Les fichiers Excel sources

Installation des Dépendances
bash
# Le pipeline installe automatiquement les packages requis :
# pandas, sqlalchemy, openpyxl, pymysql, mysql-connector-python
python etl_pipeline.py
Configuration MySQL
Modifiez les paramètres de connexion dans la fonction load_to_mysql() :

python
config = {
    'user': 'votre_utilisateur',
    'password': 'votre_mot_de_passe', 
    'host': 'localhost',
    'database': 'votre_base_donnees'
}
🚀 Utilisation
Exécution Complète
bash
python etl_pipeline.py
Étapes Automatisées
📦 Installation des Dépendances

Vérification et installation automatique des packages Python requis

📥 Chargement des Données

Lecture des fichiers Excel depuis le chemin configuré

Validation de l'existence et du format des fichiers

🧹 Nettoyage des Données

Standardisation des noms de colonnes

Gestion des valeurs manquantes

Conversion des types de données

Nettoyage des caractères spéciaux français

💾 Sauvegarde Intermédiaire

Export des données nettoyées en CSV

Encodage UTF-8 pour conservation des accents

🗄️ Chargement Base de Données

Connexion à MySQL avec gestion d'erreurs

Création des tables et clés primaires

Sauvegarde automatique des données

🎯 Segmentation RFM

Calcul des métriques Récence, Fréquence, Montant

Application de l'algorithme de segmentation

Création des segments clients

📊 Génération de Rapports

Export des segments et statistiques

Création de vues SQL pour analyse

Synthèse exécutive automatisée

📈 Segmentation RFM
Métriques Calculées
R (Récence) : Délai depuis le dernier achat

F (Fréquence) : Nombre d'achats sur la période

M (Montant) : Chiffre d'affaires généré

Segments Définis
Segment	Critères	Description
🏆 Champions	R=4, F≥3, M≥3	Clients idéaux - Forte valeur
💎 Clients Fidèles	R≥3, F≥3, M≥2	Clients réguliers et rentables
📈 Clients Potentiellement Fidèles	R≥3, F≤2, M≥2	Bonne valeur à développer
🎯 Nouveaux Clients	R≥3, F≤2, M≤2	Clients récemment acquis
⚠️ Clients Prometteurs	R=2, F≥2, M≥2	Potentiel à confirmer
🚨 À Surveiller	R=2, F≤2, M≥2	Risque de désengagement
🔴 En Voie de Désengagement	R=2, F≤2, M≤2	Clients en baisse d'activité
🔄 Clients à Regagner	R=1, F≥3, M≥3	Anciens clients de valeur
📉 Clients Perdus	R=1, F≥2, M≥2	Clients à reconquérir
👻 Fantômes Généreux	R=1, F≤2, M≥3	Clients occasionnels mais généreux
📊 Sorties et Rapports
Fichiers Générés
segmentation_rfm_complete.csv : Détail complet de tous les clients segmentés

rfm_statistics.csv : Statistiques agrégées par segment

clients_par_segment.csv : Liste des clients classés par segment

rapport_rfm_synthese.txt : Rapport exécutif de synthèse

Métriques Disponibles
Nombre de clients par segment

Chiffre d'affaires total et moyen par segment

Récence et fréquence moyennes

Pourcentage de répartition de la base client

🔧 Personnalisation
Adaptation des Chemins
Modifiez les variables base_path dans les fonctions :

load_and_clean_data() : Chemin des fichiers sources

save_cleaned_data() : Chemin des fichiers transformés

generate_rfm_report() : Chemin des rapports

Ajustement des Segments RFM
Personnalisez les règles de segmentation dans create_rfm_segmentation() :

sql
CASE
    WHEN r_score = 4 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
    -- Ajoutez vos règles personnalisées ici
END
🛠️ Dépannage
Problèmes Courants
❌ Erreur de connexion MySQL

Vérifiez que le service MySQL est démarré

Confirmez les identifiants dans la configuration

Assurez-vous que la base de données existe

❌ Fichiers Excel non trouvés

Vérifiez les chemins absolus dans le code

Confirmez l'existence des fichiers

Vérifiez les permissions de lecture

❌ Échec segmentation RFM

Vérifiez que les tables ventes et clients contiennent des données

Confirmez la présence des colonnes requises (id_client, date_vente, etc.)

📋 Validation des Résultats
Contrôles Automatiques
Vérification du nombre de lignes chargées

Validation de l'existence des tables

Contrôle de la cohérence des données RFM

Rapport d'exécution détaillé

Métriques de Qualité
Taux de complétion des données

Cohérence des segments générés

Equilibre de la répartition RFM

🔄 Maintenance
Réexécution
Le pipeline peut être réexécuté à tout moment :

Les anciennes données sont automatiquement sauvegardées

Les tables sont recréées avec les nouvelles données

L'historique est conservé dans les tables de backup

Surveillance
Logs détaillés dans la console

Rapports d'erreur complets

Statistiques d'exécution

📞 Support
Pour toute question ou problème :

Vérifiez les logs d'exécution

Confirmez la configuration MySQL

Validez le format des fichiers Excel sources
