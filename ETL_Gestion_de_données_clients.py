import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import subprocess
import sys
from datetime import datetime
²&
def install_packages():
    """Installe les packages requis"""
    packages = [
        'pandas',
        'sqlalchemy',
        'psycopg2-binary',
        'openpyxl',
        'pymysql',
        'mysql-connector-python'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Package {package} installé avec succès")
        except subprocess.CalledProcessError:
            print(f"❌ Échec de l'installation de {package}")

def load_and_clean_data():
    """Charge et nettoie les données Excel"""
    base_path = 'C:/Users/Mr ALEX/OneDrive/Bureau/Projets/Dataset ADABI Challenge/Data'
    files = {
        'ventes': os.path.join(base_path, 'ventes.xlsx'),
        'stock': os.path.join(base_path, 'stock.xlsx'),
        'achats': os.path.join(base_path, 'achats.xlsx'),
        'clients': os.path.join(base_path, 'clients.xlsx')
    }

    data = {}
    for name, path in files.items():
        try:
            data[name] = pd.read_excel(path)
            print(f"📁 {name} chargé : {data[name].shape[0]} lignes, {data[name].shape[1]} colonnes")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {name}: {str(e)}")
            return None
    return data

def clean_dataframes(data):
    """Nettoie les dataframes"""
    def clean_df(df, num_cols=None, str_cols=None, date_cols=None):
        # Nettoyage des noms de colonnes
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("é", "e").str.replace("è", "e")
        df = df.dropna(how='all').dropna(how='all', axis=1)
        
        if num_cols:
            for col in num_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].fillna(df[col].mean())
        
        if str_cols:
            for col, val in str_cols.items():
                if col in df.columns:
                    df[col] = df[col].astype(str).fillna(val)
        
        if date_cols:
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df.drop_duplicates()

    # Nettoyage avec gestion française des caractères
    data['ventes'] = clean_df(
        data['ventes'],
        num_cols=['quantite', 'prix_unitaire'],
        date_cols=['date_vente']
    )
    data['stock'] = clean_df(
        data['stock'],
        num_cols=['quantite'],
        date_cols=['date_reapprovisionnement']
    )
    data['achats'] = clean_df(
        data['achats'],
        num_cols=['quantite', 'cout_unitaire'],
        str_cols={'fournisseur': 'Inconnu'},
        date_cols=['date_achat']
    )
    data['clients'] = clean_df(
        data['clients'],
        str_cols={
            'nom': 'Inconnu',
            'email': 'no_email@example.com',
            'telephone': 'Non renseigne',
            'pays': 'Inconnu'
        },
        date_cols=['date_inscription', 'date_dernier_achat']
    )
    return data

def save_cleaned_data(data):
    """Sauvegarde les données nettoyées en CSV"""
    output_dir = "C:/Users/Mr ALEX/OneDrive/Bureau/Projets/Dataset ADABI Challenge/Data transformed"
    os.makedirs(output_dir, exist_ok=True)

    for name, df in data.items():
        output_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"💾 {name} sauvegardé dans {output_path}")

def execute_sql_safely(engine, statement, description=""):
    """Exécute une requête SQL avec gestion d'erreur"""
    try:
        with engine.connect() as connection:
            connection.execute(text(statement))
            connection.commit()
            if description:
                print(f"✅ {description}")
            return True
    except Exception as e:
        print(f"❌ Erreur {description}: {str(e)}")
        return False

def load_to_mysql():
    """Charge les données dans MySQL et exécute les requêtes SQL"""
    config = {
        'user': 'root',
        'password': 'EhDn1zpcxp@OyXJT5$r4',
        'host': 'localhost',
        'database': 'testB2'
    }

    try:
        engine_url = f"mysql+pymysql://{config['user']}:{quote_plus(config['password'])}@{config['host']}/{config['database']}"
        engine = create_engine(engine_url)

        input_dir = "C:/Users/Mr ALEX/OneDrive/Bureau/Projets/Dataset ADABI Challenge/Data transformed"
        
        # Test de connexion
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Connexion MySQL établie")

        # Configuration initiale - IMPORTANT: Désactiver toutes les contraintes
        execute_sql_safely(engine, "SET FOREIGN_KEY_CHECKS = 0;", "Désactivation des contraintes FK")
        execute_sql_safely(engine, "SET SQL_MODE = 'ALLOW_INVALID_DATES';", "Configuration SQL_MODE")
        execute_sql_safely(engine, "SET sql_mode = '';", "Configuration SQL_MODE simplifiée")
        
        # Suppression des anciennes tables si elles existent
        tables_to_drop = [
            "DROP TABLE IF EXISTS ventes_normalisees;",
            "DROP TABLE IF EXISTS segmentation_rfm;",
            "DROP TABLE IF EXISTS rfm_stats;",
            "DROP VIEW IF EXISTS rfm_stats;",
            "DROP TABLE IF EXISTS ventes_backup;",
            "DROP TABLE IF EXISTS stock_backup;",
            "DROP TABLE IF EXISTS achats_backup;",
            "DROP TABLE IF EXISTS clients_backup;",
            "DROP TABLE IF EXISTS magasins;",
            "DROP TABLE IF EXISTS produits;",
            "DROP TABLE IF EXISTS fournisseurs;"
        ]
        
        for stmt in tables_to_drop:
            execute_sql_safely(engine, stmt, "Nettoyage anciennes tables")
        
        # Chargement des fichiers CSV dans MySQL
        for file in os.listdir(input_dir):
            if file.endswith('.csv'):
                table_name = file.split('.')[0]
                df = pd.read_csv(os.path.join(input_dir, file))
                
                # Traitement spécial pour les dates
                date_columns = []
                for col in df.columns:
                    if 'date' in col.lower():
                        date_columns.append(col)
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Remplacer les NaT par NULL pour MySQL
                for col in date_columns:
                    df[col] = df[col].where(pd.notnull(df[col]), None)
                
                # Forcer les types de données pour éviter les conflits
                if table_name == 'clients':
                    # S'assurer que id_client est un entier
                    df['id_client'] = pd.to_numeric(df['id_client'], errors='coerce').fillna(0).astype(int)
                elif table_name == 'ventes':
                    # S'assurer que les IDs sont des entiers
                    df['id_client'] = pd.to_numeric(df['id_client'], errors='coerce').fillna(0).astype(int)
                    df['id_produit'] = pd.to_numeric(df['id_produit'], errors='coerce').fillna(0).astype(int)
                    df['id_magasin'] = pd.to_numeric(df['id_magasin'], errors='coerce').fillna(0).astype(int)
                
                df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, method='multi')
                print(f"🚀 {table_name} chargé dans MySQL ({len(df)} lignes)")
        
        # Correction des tables après chargement
        post_load_statements = [
            # Ajouter des clés primaires appropriées
            "ALTER TABLE clients ADD PRIMARY KEY (id_client);",
            "ALTER TABLE ventes ADD PRIMARY KEY (id_vente);",
            "ALTER TABLE stock ADD PRIMARY KEY (id_produit);",
            "ALTER TABLE achats ADD PRIMARY KEY (id_achat);"
        ]
        
        for stmt in post_load_statements:
            execute_sql_safely(engine, stmt, "Configuration des clés primaires")
        
        # Création des tables de sauvegarde APRÈS la configuration des clés primaires
        backup_tables = [
            "CREATE TABLE IF NOT EXISTS ventes_backup AS SELECT * FROM ventes;",
            "CREATE TABLE IF NOT EXISTS stock_backup AS SELECT * FROM stock;",
            "CREATE TABLE IF NOT EXISTS achats_backup AS SELECT * FROM achats;",
            "CREATE TABLE IF NOT EXISTS clients_backup AS SELECT * FROM clients;"
        ]
        
        for stmt in backup_tables:
            execute_sql_safely(engine, stmt, "Sauvegarde table")

        # Réactivation des contraintes FK seulement à la fin
        execute_sql_safely(engine, "SET FOREIGN_KEY_CHECKS = 1;", "Réactivation des contraintes FK")
        
        print("✅ Chargement MySQL terminé")
        return engine

    except Exception as e:
        print(f"❌ Erreur globale lors du chargement MySQL : {str(e)}")
        return None

def create_rfm_segmentation(engine):
    """Crée la segmentation RFM des clients"""
    print("\n🔄 Début de la segmentation RFM...")
    
    # Étape 1 : Vérification des données
    try:
        with engine.connect() as connection:
            # Vérifier les tables existantes
            result = connection.execute(text("SHOW TABLES LIKE 'ventes'"))
            if not result.fetchone():
                print("❌ Table ventes non trouvée")
                return False
            
            result = connection.execute(text("SHOW TABLES LIKE 'clients'"))
            if not result.fetchone():
                print("❌ Table clients non trouvée")
                return False
            
            # Vérifier les données et les colonnes
            result = connection.execute(text("SELECT COUNT(*) FROM ventes"))
            ventes_count = result.fetchone()[0]
            
            result = connection.execute(text("SELECT COUNT(*) FROM clients"))
            clients_count = result.fetchone()[0]
            
            # Vérifier les colonnes nécessaires
            result = connection.execute(text("SHOW COLUMNS FROM ventes"))
            ventes_columns = [row[0] for row in result.fetchall()]
            
            result = connection.execute(text("SHOW COLUMNS FROM clients"))
            clients_columns = [row[0] for row in result.fetchall()]
            
            print(f"📊 Données disponibles: {ventes_count} ventes, {clients_count} clients")
            print(f"📊 Colonnes ventes: {ventes_columns}")
            print(f"📊 Colonnes clients: {clients_columns}")
            
            if ventes_count == 0 or clients_count == 0:
                print("❌ Pas assez de données pour la segmentation RFM")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des données : {str(e)}")
        return False
    
    # Étape 2 : Suppression des anciennes tables RFM
    execute_sql_safely(engine, "SET FOREIGN_KEY_CHECKS = 0;", "Désactivation FK pour nettoyage")
    
    cleanup_statements = [
        "DROP TABLE IF EXISTS rfm_temp;",
        "DROP TABLE IF EXISTS rfm_scored;",
        "DROP TABLE IF EXISTS segmentation_rfm;",
        "DROP VIEW IF EXISTS rfm_stats;"
    ]
    
    for stmt in cleanup_statements:
        execute_sql_safely(engine, stmt, "Nettoyage des anciennes tables RFM")
    
    # Étape 3 : Création de la table RFM temporaire avec gestion des noms de colonnes
    # Adapter selon les vrais noms de colonnes de votre base
    rfm_temp_query = """
    CREATE TABLE rfm_temp AS
    SELECT
        c.id_client,
        c.nom,
        COALESCE(MAX(v.date_vente), '2020-01-01') AS derniere_vente,
        COUNT(DISTINCT v.id_vente) AS frequence,
        COALESCE(SUM(v.quantite * v.prix_unitaire), 0) AS montant_total,
        DATEDIFF(CURDATE(), COALESCE(MAX(v.date_vente), '2020-01-01')) AS recence
    FROM clients c
    LEFT JOIN ventes v ON c.id_client = v.id_client
    WHERE v.date_vente IS NOT NULL 
      AND v.date_vente != '0000-00-00'
      AND v.date_vente > '1900-01-01'
      AND v.quantite > 0
      AND v.prix_unitaire > 0
    GROUP BY c.id_client, c.nom
    HAVING frequence > 0 AND montant_total > 0;
    """
    
    if not execute_sql_safely(engine, rfm_temp_query, "Création table RFM temporaire"):
        print("❌ Échec création table RFM temporaire")
        return False
    
    # Vérifier les résultats temporaires
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM rfm_temp"))
            temp_count = result.fetchone()[0]
            print(f"📊 {temp_count} clients avec historique de ventes")
            
            if temp_count == 0:
                print("❌ Aucun client avec historique de ventes valide")
                # Essayer une version plus permissive
                rfm_temp_query_alt = """
                CREATE TABLE rfm_temp AS
                SELECT
                    c.id_client,
                    c.nom,
                    COALESCE(MAX(v.date_vente), CURDATE()) AS derniere_vente,
                    COUNT(v.id_vente) AS frequence,
                    COALESCE(SUM(v.quantite * v.prix_unitaire), 0) AS montant_total,
                    DATEDIFF(CURDATE(), COALESCE(MAX(v.date_vente), CURDATE())) AS recence
                FROM clients c
                LEFT JOIN ventes v ON c.id_client = v.id_client
                GROUP BY c.id_client, c.nom
                HAVING frequence > 0;
                """
                
                execute_sql_safely(engine, "DROP TABLE IF EXISTS rfm_temp;", "Suppression table temp")
                if not execute_sql_safely(engine, rfm_temp_query_alt, "Création table RFM temporaire"):
                    return False
                
                # Revérifier
                result = connection.execute(text("SELECT COUNT(*) FROM rfm_temp"))
                temp_count = result.fetchone()[0]
                print(f"📊 {temp_count} clients avec historique (version alternative)")
                
                if temp_count == 0:
                    return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification temporaire : {str(e)}")
        return False
    
    # Étape 4 : Calcul des scores RFM avec NTILE
    rfm_scored_query = """
    CREATE TABLE rfm_scored AS
    SELECT
        r.*,
        NTILE(4) OVER (ORDER BY recence DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequence ASC) AS f_score,
        NTILE(4) OVER (ORDER BY montant_total ASC) AS m_score
    FROM rfm_temp r;
    """
    
    if not execute_sql_safely(engine, rfm_scored_query, "Calcul des scores RFM"):
        return False
    
    # Étape 5 : Segmentation finale
    segmentation_query = """
    CREATE TABLE segmentation_rfm AS
    SELECT
        *,
        CONCAT(r_score, f_score, m_score) AS rfm_score,
        CASE
            WHEN r_score = 4 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 2 THEN 'Clients fidèles'
            WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 2 THEN 'Clients potentiellement fidèles'
            WHEN r_score >= 3 AND f_score <= 2 AND m_score <= 2 THEN 'Nouveaux clients'
            WHEN r_score = 2 AND f_score >= 2 AND m_score >= 2 THEN 'Clients prometteurs'
            WHEN r_score = 2 AND f_score <= 2 AND m_score >= 2 THEN 'À surveiller'
            WHEN r_score = 2 AND f_score <= 2 AND m_score <= 2 THEN 'En voie de désengagement'
            WHEN r_score = 1 AND f_score >= 3 AND m_score >= 3 THEN 'Clients à regagner'
            WHEN r_score = 1 AND f_score >= 2 AND m_score >= 2 THEN 'Clients perdus'
            WHEN r_score = 1 AND f_score <= 2 AND m_score >= 3 THEN 'Fantomes Genereux'
            WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Evaporés'
            ELSE 'Autres'
        END AS segment
    FROM rfm_scored;
    """
    
    if not execute_sql_safely(engine, segmentation_query, "Création de la segmentation"):
        return False
    
    # Étape 6 : Création de la vue statistiques
    stats_view_query = """
    CREATE VIEW rfm_stats AS
    SELECT
        segment,
        COUNT(*) as nombre_clients,
        ROUND(AVG(recence), 1) as recence_moyenne,
        ROUND(AVG(frequence), 1) as frequence_moyenne,
        ROUND(AVG(montant_total), 2) as montant_moyen,
        ROUND(SUM(montant_total), 2) as chiffre_affaires_total,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM segmentation_rfm), 2) as pourcentage
    FROM segmentation_rfm
    GROUP BY segment
    ORDER BY chiffre_affaires_total DESC;
    """
    
    if not execute_sql_safely(engine, stats_view_query, "Création vue statistiques"):
        return False
    
    # Étape 7 : Affichage des résultats
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM rfm_stats"))
            rfm_results = result.fetchall()
            
            print("\n📊 Résumé de la segmentation RFM :")
            print("-" * 100)
            print(f"{'Segment':<20} | {'Clients':<8} | {'%':<6} | {'CA Total':<15} | {'Récence':<8} | {'Fréquence':<10}")
            print("-" * 100)
            for row in rfm_results:
                print(f"{row[0]:<20} | {row[1]:<8} | {row[6]:<6.1f}% | {row[5]:>12,.2f}€ | {row[2]:<8} | {row[3]:<10}")
            print("-" * 100)
            
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des résultats : {str(e)}")
        return False
    
    # Nettoyage des tables temporaires
    execute_sql_safely(engine, "DROP TABLE IF EXISTS rfm_temp;", "Nettoyage table temporaire")
    execute_sql_safely(engine, "DROP TABLE IF EXISTS rfm_scored;", "Nettoyage table scored")
    execute_sql_safely(engine, "SET FOREIGN_KEY_CHECKS = 1;", "Réactivation FK")
    
    print("✅ Segmentation RFM terminée avec succès")
    return True
    return True

def generate_rfm_report(engine):
    """Génère un rapport détaillé de la segmentation RFM"""
    print("\n📈 Génération du rapport RFM...")
    
    output_dir = "C:/Users/Mr ALEX/OneDrive/Bureau/Projets/Dataset ADABI Challenge/RFM_Results"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Export de la segmentation complète
        try:
            df_rfm = pd.read_sql("SELECT * FROM segmentation_rfm ORDER BY montant_total DESC", engine)
            rfm_file = os.path.join(output_dir, "segmentation_rfm_complete.csv")
            df_rfm.to_csv(rfm_file, index=False, encoding='utf-8-sig')
            print(f"✅ Segmentation complète exportée : {len(df_rfm)} clients")
        except Exception as e:
            print(f"❌ Erreur export segmentation complète : {str(e)}")
        
        # Export des statistiques par segment
        try:
            df_stats = pd.read_sql("SELECT * FROM rfm_stats", engine)
            stats_file = os.path.join(output_dir, "rfm_statistics.csv")
            df_stats.to_csv(stats_file, index=False, encoding='utf-8-sig')
            print(f"✅ Statistiques RFM exportées : {len(df_stats)} segments")
        except Exception as e:
            print(f"❌ Erreur export statistiques : {str(e)}")
        
        # Export des clients par segment (top 10 de chaque segment)
        try:
            segments_query = """
            SELECT segment, id_client, nom, recence, frequence, montant_total, rfm_score
            FROM segmentation_rfm 
            ORDER BY segment, montant_total DESC
            """
            df_segments = pd.read_sql(segments_query, engine)
            segments_file = os.path.join(output_dir, "clients_par_segment.csv")
            df_segments.to_csv(segments_file, index=False, encoding='utf-8-sig')
            print(f"✅ Détail par segment exporté : {len(df_segments)} clients")
        except Exception as e:
            print(f"❌ Erreur export détail segments : {str(e)}")
        
        # Création d'un rapport de synthèse
        try:
            rapport_file = os.path.join(output_dir, "rapport_rfm_synthese.txt")
            with open(rapport_file, 'w', encoding='utf-8') as f:
                f.write("RAPPORT DE SEGMENTATION RFM\n")
                f.write("=" * 50 + "\n")
                f.write(f"Date de génération : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Statistiques globales
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT COUNT(*) FROM segmentation_rfm"))
                    total_clients = result.fetchone()[0]
                    
                    result = connection.execute(text("SELECT SUM(montant_total) FROM segmentation_rfm"))
                    ca_total = result.fetchone()[0]
                    
                    f.write(f"Nombre total de clients analysés : {total_clients}\n")
                    f.write(f"Chiffre d'affaires total : {ca_total:,.2f}€\n\n")
                    
                    # Détail par segment
                    result = connection.execute(text("SELECT * FROM rfm_stats"))
                    segments = result.fetchall()
                    
                    f.write("RÉPARTITION PAR SEGMENT :\n")
                    f.write("-" * 30 + "\n")
                    for segment in segments:
                        f.write(f"{segment[0]} :\n")
                        f.write(f"  - Clients : {segment[1]} ({segment[6]:.1f}%)\n")
                        f.write(f"  - CA : {segment[5]:,.2f}€\n")
                        f.write(f"  - Récence moyenne : {segment[2]} jours\n")
                        f.write(f"  - Fréquence moyenne : {segment[3]} achats\n")
                        f.write(f"  - Montant moyen : {segment[4]:,.2f}€\n\n")
            
            print(f"✅ Rapport de synthèse créé")
            
        except Exception as e:
            print(f"❌ Erreur création rapport synthèse : {str(e)}")
        
        print(f"📈 Tous les rapports RFM ont été exportés dans : {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport : {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage du pipeline ETL avec segmentation RFM")
    print("=" * 60)
    
    # Installation des packages
    print("\n📦 Installation des packages...")
    install_packages()
    
    # Chargement et nettoyage des données
    print("\n📊 Chargement et nettoyage des données...")
    data = load_and_clean_data()
    
    if data:
        # Nettoyage des dataframes
        print("\n🧹 Nettoyage des dataframes...")
        data = clean_dataframes(data)
        
        # Sauvegarde en CSV
        print("\n💾 Sauvegarde des données nettoyées...")
        save_cleaned_data(data)
        
        # Chargement en base
        print("\n🔄 Chargement en base MySQL...")
        engine = load_to_mysql()
        
        if engine:
            # Segmentation RFM
            print("\n🎯 Segmentation RFM...")
            if create_rfm_segmentation(engine):
                
                # Génération du rapport RFM
                print("\n📈 Génération du rapport RFM...")
                generate_rfm_report(engine)
                
                print("\n✅ Pipeline ETL terminé avec succès !")
            else:
                print("\n❌ Échec de la segmentation RFM")
        else:
            print("\n❌ Échec du chargement en base")
    else:
        print("❌ Échec du chargement des données")