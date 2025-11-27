"""
Event Log Builder pour Manufacturing Operations Radar
Génère un event log réaliste à partir des données MES, PLM et ERP
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path
from typing import List, Dict


class EventLogBuilder:
    """Construit un event log cohérent à partir des données réelles"""

    def __init__(self, plm_data: Dict, mes_data: pd.DataFrame, erp_data: pd.DataFrame):
        self.plm_data = plm_data
        self.mes_data = mes_data
        self.erp_data = erp_data
        self.event_log = []

    def parse_time_duration(self, time_str: str) -> float:
        """Convertit une durée au format 'XXh YYmin' en heures"""
        if pd.isna(time_str) or time_str == '':
            return 0.0

        time_str = str(time_str).strip()
        hours = 0.0
        minutes = 0.0

        # Gérer format "XXh YYmin"
        if 'h' in time_str:
            parts = time_str.split('h')
            hours = float(parts[0].strip())
            if len(parts) > 1 and 'min' in parts[1]:
                minutes = float(parts[1].replace('min', '').strip())
        elif 'min' in time_str:
            minutes = float(time_str.replace('min', '').strip())
        else:
            # Essayer de parser comme nombre
            try:
                hours = float(time_str)
            except:
                hours = 0.0

        return hours + (minutes / 60.0)

    def get_operation_sequence(self) -> List[str]:
        """Définit la séquence d'opérations à partir du MES"""
        # Extraire les noms d'opérations uniques
        operations = self.mes_data['Nom'].unique().tolist()

        # Définir une chaîne de production logique (4-8 opérations principales)
        # On sélectionne les opérations les plus représentatives
        operation_counts = self.mes_data['Nom'].value_counts()

        # Prendre les opérations les plus fréquentes pour construire la chaîne
        main_operations = operation_counts.head(8).index.tolist()

        print(f"🔧 Chaîne de production identifiée: {len(main_operations)} opérations")
        for i, op in enumerate(main_operations, 1):
            count = operation_counts[op]
            print(f"  {i}. {op} ({count} enregistrements)")

        return main_operations

    def get_operation_stats(self, operation_name: str) -> Dict:
        """Récupère les statistiques d'une opération depuis le MES"""
        op_data = self.mes_data[self.mes_data['Nom'] == operation_name]

        if len(op_data) == 0:
            return {
                'temps_prevu_moyen': 2.0,
                'temps_reel_moyen': 2.2,
                'variabilite': 0.3,
                'taux_alea': 0.1
            }

        # Parser les temps
        temps_prevus = op_data['Temps Prévu'].apply(self.parse_time_duration)
        temps_reels = op_data['Temps Réel'].apply(self.parse_time_duration)

        # Calculer les stats
        temps_prevu_moyen = temps_prevus.mean()
        temps_reel_moyen = temps_reels.mean()
        variabilite = temps_reels.std() / temps_reel_moyen if temps_reel_moyen > 0 else 0.3
        taux_alea = op_data['Aléas Industriels'].notna().sum() / len(op_data)

        return {
            'temps_prevu_moyen': temps_prevu_moyen,
            'temps_reel_moyen': temps_reel_moyen,
            'variabilite': variabilite,
            'taux_alea': taux_alea,
            'sample_data': op_data.iloc[0] if len(op_data) > 0 else None
        }

    def assign_resource(self, operation_name: str, station_id: int) -> Dict:
        """Assigne un opérateur depuis l'ERP"""
        # Trouver les opérateurs disponibles pour ce poste
        poste_name = f"Poste {station_id}"
        available_operators = self.erp_data[
            self.erp_data['Poste de montage'] == poste_name
        ]

        if len(available_operators) == 0:
            # Fallback: prendre un opérateur au hasard
            available_operators = self.erp_data

        # Sélectionner un opérateur aléatoire
        operator = available_operators.sample(1).iloc[0]

        return {
            'resource_id': operator['Matricule'],
            'resource_name': f"{operator['Prénom']} {operator['Nom']}",
            'qualification': operator['Qualification'],
            'cout_horaire': operator['Coût horaire (€)']
        }

    def determine_result(self, operation_stats: Dict) -> str:
        """Détermine le résultat d'une opération (OK/Rework/NOK)"""
        # Basé sur le taux d'aléas observé
        taux_alea = operation_stats['taux_alea']

        rand = random.random()

        if rand < 0.90:  # 90% OK
            return 'OK'
        elif rand < 0.90 + (taux_alea * 0.7):  # ~7% Rework
            return 'Rework'
        else:  # ~3% NOK
            return 'NOK'

    def calculate_wait_time(self, operation_idx: int, operations: List[str],
                           current_wip: Dict) -> float:
        """Calcule le temps d'attente basé sur le WIP actuel"""
        operation = operations[operation_idx]

        # Certaines opérations sont des goulots (plus de WIP = plus d'attente)
        # On crée artificiellement des goulots sur certaines opérations
        is_bottleneck = operation_idx in [2, 4]  # Opérations 3 et 5 sont des goulots

        base_wait = 0.1  # 6 minutes de base

        if is_bottleneck:
            wip_count = current_wip.get(operation, 0)
            # Temps d'attente augmente avec le WIP
            wait_time = base_wait + (wip_count * 0.3)  # +18 min par pièce en attente
        else:
            wait_time = base_wait * random.uniform(0.5, 1.5)

        return wait_time

    def generate_event_log(self, num_cases: int = 100,
                          start_date: datetime = None) -> pd.DataFrame:
        """Génère l'event log complet"""
        if start_date is None:
            start_date = datetime(2023, 9, 1, 8, 0, 0)  # Début des données MES

        print(f"\n🏭 GÉNÉRATION DE L'EVENT LOG")
        print("=" * 60)
        print(f"Nombre de pièces (cases): {num_cases}")

        # Obtenir la séquence d'opérations
        operations = self.get_operation_sequence()

        # Statistiques par opération
        operation_stats = {}
        for op in operations:
            operation_stats[op] = self.get_operation_stats(op)

        # Obtenir les références de pièces depuis PLM
        plm_sheet1 = self.plm_data['Sheet1']
        piece_references = plm_sheet1['Code / Référence'].unique().tolist()

        # Générer les cases
        events = []
        current_wip = {op: 0 for op in operations}

        for case_idx in range(num_cases):
            case_id = f"P{case_idx:04d}"
            reference = random.choice(piece_references)

            # Timestamp de départ pour cette pièce
            # Ajouter un offset pour étaler les arrivées
            case_start = start_date + timedelta(hours=case_idx * 0.5)
            current_timestamp = case_start

            # La pièce passe par toutes les opérations
            for op_idx, operation in enumerate(operations):
                stats = operation_stats[operation]

                # Temps d'attente avant l'opération
                wait_time = self.calculate_wait_time(op_idx, operations, current_wip)

                # Incrémenter le WIP
                current_wip[operation] += 1

                # Timestamp de début
                timestamp_start = current_timestamp + timedelta(hours=wait_time)

                # Calculer la durée de l'opération (avec variabilité)
                base_time = stats['temps_reel_moyen']
                variability = stats['variabilite']
                actual_time = base_time * random.uniform(
                    1 - variability,
                    1 + variability
                )

                # Timestamp de fin
                timestamp_end = timestamp_start + timedelta(hours=actual_time)

                # Station ID (rotation entre postes)
                station_id = (op_idx * 7 + 1) % 56 + 1  # Rotation sur les 56 postes

                # Assigner une ressource
                resource = self.assign_resource(operation, station_id)

                # Déterminer le résultat
                result = self.determine_result(stats)

                # Aléa industriel ?
                has_alea = random.random() < stats['taux_alea']
                alea = None
                if has_alea and stats['sample_data'] is not None:
                    alea = stats['sample_data']['Aléas Industriels']

                # Créer l'événement
                event = {
                    'case_id': case_id,
                    'activity': operation,
                    'timestamp_start': timestamp_start,
                    'timestamp_end': timestamp_end,
                    'station_id': f"Station_{station_id}",
                    'resource_id': resource['resource_id'],
                    'resource_name': resource['resource_name'],
                    'qualification': resource['qualification'],
                    'result': result,
                    'rework_flag': result == 'Rework',
                    'reference': reference,
                    'temps_prevu': stats['temps_prevu_moyen'],
                    'temps_reel': actual_time,
                    'wait_time': wait_time,
                    'alea': alea if has_alea else None,
                    'cout_horaire': resource['cout_horaire']
                }

                events.append(event)

                # Décrémenter le WIP
                current_wip[operation] -= 1

                # Si rework, ajouter un passage supplémentaire
                if result == 'Rework':
                    # La pièce repasse par l'opération précédente ou la même
                    rework_op = operation
                    rework_timestamp_start = timestamp_end + timedelta(hours=0.5)
                    rework_actual_time = actual_time * 0.8  # Le rework est plus rapide

                    rework_event = {
                        'case_id': case_id,
                        'activity': f"{rework_op}_Rework",
                        'timestamp_start': rework_timestamp_start,
                        'timestamp_end': rework_timestamp_start + timedelta(hours=rework_actual_time),
                        'station_id': f"Station_{station_id}",
                        'resource_id': resource['resource_id'],
                        'resource_name': resource['resource_name'],
                        'qualification': resource['qualification'],
                        'result': 'OK',  # Le rework réussit
                        'rework_flag': True,
                        'reference': reference,
                        'temps_prevu': stats['temps_prevu_moyen'] * 0.8,
                        'temps_reel': rework_actual_time,
                        'wait_time': 0.5,
                        'alea': 'Rework nécessaire',
                        'cout_horaire': resource['cout_horaire']
                    }

                    events.append(rework_event)
                    current_timestamp = rework_timestamp_start + timedelta(hours=rework_actual_time)
                else:
                    current_timestamp = timestamp_end

        # Créer le DataFrame
        event_log_df = pd.DataFrame(events)

        # Trier par timestamp_start
        event_log_df = event_log_df.sort_values('timestamp_start').reset_index(drop=True)

        print(f"\n✅ Event log généré!")
        print(f"  - Nombre total d'événements: {len(event_log_df)}")
        print(f"  - Nombre de cases (pièces): {event_log_df['case_id'].nunique()}")
        print(f"  - Nombre d'opérations: {event_log_df['activity'].nunique()}")
        print(f"  - Période: {event_log_df['timestamp_start'].min()} → {event_log_df['timestamp_end'].max()}")
        print(f"  - Taux de rework: {event_log_df['rework_flag'].mean()*100:.1f}%")

        return event_log_df

    def save_event_log(self, event_log_df: pd.DataFrame, output_path: str):
        """Sauvegarde l'event log"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sauvegarder en CSV
        csv_path = output_path.with_suffix('.csv')
        event_log_df.to_csv(csv_path, index=False)
        print(f"\n💾 Event log sauvegardé: {csv_path}")

        # Sauvegarder en Excel aussi
        excel_path = output_path.with_suffix('.xlsx')
        event_log_df.to_excel(excel_path, index=False)
        print(f"💾 Event log sauvegardé: {excel_path}")

        return csv_path


if __name__ == "__main__":
    from data_loader import DataLoader

    # Charger les données
    loader = DataLoader()
    plm, mes, erp = loader.load_all_data()

    # Créer le builder
    builder = EventLogBuilder(plm, mes, erp)

    # Générer l'event log
    event_log = builder.generate_event_log(num_cases=150)

    # Sauvegarder
    builder.save_event_log(event_log, "data/event_logs/manufacturing_event_log.csv")

    # Afficher un aperçu
    print("\n📊 APERÇU DE L'EVENT LOG")
    print("=" * 60)
    print(event_log.head(20))

    print("\n📊 STATISTIQUES PAR OPÉRATION")
    print("=" * 60)
    stats = event_log.groupby('activity').agg({
        'case_id': 'count',
        'temps_reel': 'mean',
        'wait_time': 'mean',
        'rework_flag': 'sum'
    }).round(2)
    stats.columns = ['Nombre événements', 'Temps réel moyen (h)', 'Temps attente moyen (h)', 'Nombre reworks']
    print(stats)
