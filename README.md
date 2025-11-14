
# 📊 Pipeline de Traitement de Données Client avec Segmentation RFM

## 🎯 Description du Projet
Ce **pipeline ETL (Extract, Transform, Load)** automatise le traitement des données commerciales et implémente une **segmentation RFM** (Récence, Fréquence, Montant) pour analyser la valeur et le comportement des clients.

Le processus transforme des fichiers Excel bruts en **segments clients actionnables**, prêts pour l’analyse et la visualisation dans **Power BI**.

---

## 🔄 Architecture du Pipeline

**Flux de Données :**  
```

Fichiers Excel → Nettoyage → CSV Intermédiaires → Base MySQL → Calcul RFM → Segments Clients → Rapports → Power BI

````

---

## 📁 Structure des Fichiers

### Données d'entrée (à placer dans le dossier spécifié)
- `ventes.xlsx` – Données des transactions commerciales  
- `clients.xlsx` – Informations sur les clients  
- `stock.xlsx` – Données d’inventaire et de stock  
- `achats.xlsx` – Données des approvisionnements  

### Sorties générées
- Données nettoyées : CSV dans le dossier `Data_transformed`  
- Base de données : Tables MySQL avec métriques RFM  
- Rapports RFM : CSV et synthèses dans `RFM_Results`  

---

## ⚙️ Installation et Configuration

### Prérequis
- Python 3.7+  
- MySQL Server  
- Fichiers Excel sources  

### Installation des Dépendances
```bash
# Le pipeline installe automatiquement les packages requis :
# pandas, sqlalchemy, openpyxl, pymysql, mysql-connector-python
python etl_pipeline.py
````

### Configuration MySQL

Modifiez les paramètres de connexion dans la fonction `load_to_mysql()` :

```python
config = {
    'user': 'votre_utilisateur',
    'password': 'votre_mot_de_passe',
    'host': 'localhost',
    'database': 'votre_base_donnees'
}
```

---

## 🚀 Utilisation

### Exécution Complète

```bash
python etl_pipeline.py
```

### Étapes Automatisées

1. **📦 Installation des dépendances** : Vérification et installation automatique des packages Python requis
2. **📥 Chargement des données** : Lecture et validation des fichiers Excel
3. **🧹 Nettoyage des données** : Standardisation des colonnes, gestion des valeurs manquantes, nettoyage des caractères spéciaux français
4. **💾 Sauvegarde intermédiaire** : Export en CSV encodés UTF-8
5. **🗄️ Chargement Base de Données** : Création des tables MySQL et insertion des données
6. **🎯 Segmentation RFM** : Calcul des métriques Récence, Fréquence, Montant et création des segments clients
7. **📊 Génération de rapports** : Export des segments, statistiques et synthèse exécutive

---

## 📈 Segmentation RFM

### Métriques Calculées

* **R (Récence)** : Délai depuis le dernier achat
* **F (Fréquence)** : Nombre d'achats sur la période
* **M (Montant)** : Chiffre d'affaires généré

### Segments Définis

| Segment                            | Critères      | Description                        |
| ---------------------------------- | ------------- | ---------------------------------- |
| 🏆 Champions                       | R=4, F≥3, M≥3 | Clients idéaux - Forte valeur      |
| 💎 Clients Fidèles                 | R≥3, F≥3, M≥2 | Clients réguliers et rentables     |
| 📈 Clients Potentiellement Fidèles | R≥3, F≤2, M≥2 | Bonne valeur à développer          |
| 🎯 Nouveaux Clients                | R≥3, F≤2, M≤2 | Clients récemment acquis           |
| ⚠️ Clients Prometteurs             | R=2, F≥2, M≥2 | Potentiel à confirmer              |
| 🚨 À Surveiller                    | R=2, F≤2, M≥2 | Risque de désengagement            |
| 🔴 En Voie de Désengagement        | R=2, F≤2, M≤2 | Clients en baisse d’activité       |
| 🔄 Clients à Regagner              | R=1, F≥3, M≥3 | Anciens clients de valeur          |
| 📉 Clients Perdus                  | R=1, F≥2, M≥2 | Clients à reconquérir              |
| 👻 Fantômes Généreux               | R=1, F≤2, M≥3 | Clients occasionnels mais généreux |

---

## 📊 Sorties et Rapports

### Fichiers générés

* `segmentation_rfm_complete.csv` : Détail complet des clients segmentés
* `rfm_statistics.csv` : Statistiques agrégées par segment
* `clients_par_segment.csv` : Liste des clients classés par segment
* `rapport_rfm_synthese.txt` : Rapport exécutif synthétique

### Métriques disponibles

* Nombre de clients par segment
* Chiffre d’affaires total et moyen par segment
* Récence et fréquence moyennes
* Pourcentage de répartition de la base client

---

## 🔧 Personnalisation

### Adaptation des chemins

Modifiez les variables `base_path` dans les fonctions :

* `load_and_clean_data()` : Chemin des fichiers sources
* `save_cleaned_data()` : Chemin des fichiers transformés
* `generate_rfm_report()` : Chemin des rapports

### Ajustement des segments RFM

Personnalisez les règles de segmentation dans `create_rfm_segmentation()` :

```sql
CASE
    WHEN r_score = 4 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
    -- Ajoutez vos règles personnalisées ici
END
```

---

## 🛠️ Dépannage

### Problèmes courants

* ❌ **Erreur de connexion MySQL** : Vérifiez que le service MySQL est actif et les identifiants corrects
* ❌ **Fichiers Excel non trouvés** : Confirmez les chemins et permissions de lecture
* ❌ **Échec segmentation RFM** : Vérifiez que les tables `ventes` et `clients` contiennent des données et colonnes requises

---

## 📋 Validation des résultats

* Vérification du nombre de lignes chargées
* Validation de l’existence des tables
* Contrôle de cohérence des données RFM
* Rapport d’exécution détaillé
* Métriques de qualité : taux de complétion, cohérence et équilibre des segments

---

## 🔄 Maintenance

* **Réexécution** : Le pipeline peut être réexécuté à tout moment. Les anciennes données sont sauvegardées, les tables recréées, et l’historique conservé
* **Surveillance** : Logs détaillés dans la console, rapports d’erreur et statistiques d’exécution

---

## 📞 Support

* Vérifiez les logs d’exécution
* Confirmez la configuration MySQL
* Validez le format des fichiers Excel sources


