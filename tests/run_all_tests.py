"""
Script principal pour exécuter tous les tests de validation
Génère un rapport complet de validation
"""

import sys
import pytest
from pathlib import Path
from datetime import datetime
import subprocess


def run_tests():
    """Exécute tous les tests et génère un rapport"""

    print("=" * 80)
    print("🧪 MANUFACTURING OPERATIONS RADAR - SUITE DE TESTS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Liste des suites de tests
    test_suites = [
        ("test_data_loader.py", "Validation du chargement des données"),
        ("test_event_log_builder.py", "Validation de la génération de l'event log"),
        ("test_analysis.py", "Validation des modules d'analyse"),
        ("test_integration.py", "Tests d'intégration end-to-end"),
    ]

    results = []
    total_passed = 0
    total_failed = 0

    # Exécuter chaque suite de tests
    for test_file, description in test_suites:
        print(f"\n{'='*80}")
        print(f"📋 {description}")
        print(f"   Fichier: {test_file}")
        print(f"{'='*80}\n")

        # Exécuter les tests avec pytest
        result = pytest.main([
            test_file,
            "-v",
            "--tb=short",
            "--color=yes"
        ])

        results.append({
            "file": test_file,
            "description": description,
            "result": result
        })

        if result == 0:
            print(f"\n✅ {description} - SUCCÈS")
        else:
            print(f"\n❌ {description} - ÉCHEC")

    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80 + "\n")

    for res in results:
        status = "✅ PASS" if res["result"] == 0 else "❌ FAIL"
        print(f"{status} - {res['description']}")

    # Compter les résultats
    passed = sum(1 for r in results if r["result"] == 0)
    failed = len(results) - passed

    print(f"\n📈 Résultats globaux:")
    print(f"   ✅ Suites réussies: {passed}/{len(results)}")
    print(f"   ❌ Suites échouées: {failed}/{len(results)}")

    success_rate = (passed / len(results)) * 100
    print(f"   📊 Taux de réussite: {success_rate:.1f}%")

    # Générer un rapport texte
    report_path = Path("outputs/reports/test_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("RAPPORT DE VALIDATION - MANUFACTURING OPERATIONS RADAR\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("RÉSULTATS PAR SUITE:\n")
        f.write("-" * 80 + "\n")
        for res in results:
            status = "PASS" if res["result"] == 0 else "FAIL"
            f.write(f"[{status}] {res['description']}\n")
            f.write(f"      Fichier: {res['file']}\n\n")

        f.write("RÉSUMÉ GLOBAL:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Suites réussies: {passed}/{len(results)}\n")
        f.write(f"Suites échouées: {failed}/{len(results)}\n")
        f.write(f"Taux de réussite: {success_rate:.1f}%\n")

    print(f"\n💾 Rapport sauvegardé: {report_path}")

    print("\n" + "=" * 80)
    if failed == 0:
        print("✅ TOUS LES TESTS SONT PASSÉS - SYSTÈME VALIDÉ")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFIER LES DÉTAILS")
    print("=" * 80 + "\n")

    return 0 if failed == 0 else 1


def check_prerequisites():
    """Vérifie les prérequis avant d'exécuter les tests"""

    print("🔍 Vérification des prérequis...")

    # Vérifier que les fichiers de données existent
    data_files = [
        "data/raw/PLM_DataSet.xlsx",
        "data/raw/MES_Extraction.xlsx",
        "data/raw/ERP_Equipes Airplus.xlsx"
    ]

    missing_files = []
    for file in data_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("❌ Fichiers manquants:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n⚠️  Veuillez vous assurer que les fichiers de données sont présents.")
        return False

    # Vérifier que l'event log a été généré
    event_log_path = Path("data/event_logs/manufacturing_event_log.csv")
    if not event_log_path.exists():
        print("⚠️  Event log non trouvé. Génération en cours...")
        try:
            sys.path.append(str(Path(__file__).parent.parent / "src"))
            from data_processing.data_loader import DataLoader
            from data_processing.event_log_builder import EventLogBuilder

            loader = DataLoader("data/raw")
            plm, mes, erp = loader.load_all_data()
            builder = EventLogBuilder(plm, mes, erp)
            event_log = builder.generate_event_log(num_cases=150)
            builder.save_event_log(event_log, "data/event_logs/manufacturing_event_log.csv")
            print("✅ Event log généré")
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'event log: {e}")
            return False

    # Vérifier que les analyses ont été exécutées
    required_outputs = [
        "outputs/reports/kpis_summary.json",
        "outputs/recommendations/recommendations.json"
    ]

    missing_outputs = []
    for output in required_outputs:
        if not Path(output).exists():
            missing_outputs.append(output)

    if missing_outputs:
        print("⚠️  Certains fichiers de sortie sont manquants. Exécution des analyses...")
        try:
            # Exécuter les analyses
            from analysis.analyze_all import run_complete_analysis
            from optimization.run_optimization import run_optimization_analysis

            run_complete_analysis("data/event_logs/manufacturing_event_log.csv")
            run_optimization_analysis("data/event_logs/manufacturing_event_log.csv")
            print("✅ Analyses exécutées")
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des analyses: {e}")
            print("⚠️  Certains tests d'intégration pourraient échouer")

    print("✅ Prérequis vérifiés\n")
    return True


if __name__ == "__main__":
    # Vérifier les prérequis
    if not check_prerequisites():
        print("\n❌ Prérequis non satisfaits. Veuillez corriger les problèmes ci-dessus.")
        sys.exit(1)

    # Exécuter les tests
    exit_code = run_tests()
    sys.exit(exit_code)
