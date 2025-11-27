"""
Manufacturing Optimizer pour Operations Radar
Moteur d'optimisation et génération de recommandations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from analysis.process_mining import ProcessMiner
from analysis.bottleneck_detector import BottleneckDetector
from analysis.wip_analyzer import WIPAnalyzer
from analysis.rework_tracker import ReworkTracker


class ManufacturingOptimizer:
    """Moteur d'optimisation pour la chaîne de production"""

    def __init__(self, event_log: pd.DataFrame):
        self.event_log = event_log.copy()
        self.baseline_kpis = None
        self._calculate_baseline()

    def _calculate_baseline(self):
        """Calcule les KPIs de base"""
        pm = ProcessMiner(self.event_log)
        wip = WIPAnalyzer(self.event_log)
        rt = ReworkTracker(self.event_log)

        overview = pm.get_process_overview()
        inventory = wip.calculate_inventory_profile()
        flow_eff = wip.calculate_flow_efficiency()
        rework_summary = rt.get_rework_summary()

        self.baseline_kpis = {
            'lead_time_mean': overview['lead_time_moyen'],
            'lead_time_std': overview['lead_time_std'],
            'wip_mean': inventory['actual_wip'],
            'throughput': overview['throughput'],
            'rework_rate': overview['taux_rework'],
            'flow_efficiency': flow_eff['avg_flow_efficiency'],
            'rework_cost': rework_summary.get('total_rework_cost_euros', 0)
        }

    def identify_optimization_opportunities(self) -> Dict:
        """Identifie toutes les opportunités d'amélioration"""

        print("\n🔍 IDENTIFICATION DES OPPORTUNITÉS D'OPTIMISATION")
        print("=" * 80)

        bd = BottleneckDetector(self.event_log)
        wip = WIPAnalyzer(self.event_log)
        rt = ReworkTracker(self.event_log)

        opportunities = {}

        # 1. Goulots d'étranglement
        print("\n1️⃣ Analyse des goulots d'étranglement...")
        bottlenecks = bd.detect_bottlenecks_by_wait_time()
        top_bottlenecks = bottlenecks[bottlenecks['is_bottleneck']].head(3)

        opportunities['bottlenecks'] = []
        for _, bn in top_bottlenecks.iterrows():
            opp = {
                'type': 'bottleneck',
                'activity': bn['activity'],
                'wait_time_mean': bn['wait_time_mean'],
                'cycle_time_mean': bn['cycle_time_mean'],
                'wait_to_cycle_ratio': bn['wait_to_cycle_ratio'],
                'impact_pct': bn['wait_time_impact_pct']
            }
            opportunities['bottlenecks'].append(opp)
            print(f"   ⚠️  {bn['activity']}: ratio attente/cycle = {bn['wait_to_cycle_ratio']:.2f}")

        # 2. Points d'accumulation de WIP
        print("\n2️⃣ Analyse des accumulations de WIP...")
        wip_accumulations = wip.identify_wip_accumulation_points()

        opportunities['wip_accumulations'] = []
        for _, acc in wip_accumulations.head(3).iterrows():
            opp = {
                'type': 'wip_accumulation',
                'activity': acc['activity'],
                'wip_mean': acc['wip_mean'],
                'wip_excess': acc['wip_excess'],
                'wip_excess_pct': acc['wip_excess_pct']
            }
            opportunities['wip_accumulations'].append(opp)
            print(f"   📦 {acc['activity']}: excès WIP = +{acc['wip_excess_pct']:.1f}%")

        # 3. Problèmes de rework
        print("\n3️⃣ Analyse des reworks...")
        rework_rate = rt.calculate_rework_rate_by_activity()
        high_rework = rework_rate.nlargest(3, 'rework_rate_pct')

        opportunities['high_rework'] = []
        for _, rw in high_rework.iterrows():
            opp = {
                'type': 'high_rework',
                'activity': rw['activity'],
                'rework_rate_pct': rw['rework_rate_pct'],
                'rework_events': rw['rework_events'],
                'total_events': rw['total_events']
            }
            opportunities['high_rework'].append(opp)
            print(f"   🔄 {rw['activity']}: taux rework = {rw['rework_rate_pct']:.1f}%")

        # 4. Faible efficacité du flux
        flow_eff = wip.calculate_flow_efficiency()
        if flow_eff['avg_flow_efficiency'] < 50:
            print(f"\n4️⃣ Faible efficacité du flux: {flow_eff['avg_flow_efficiency']:.1f}%")
            opportunities['low_flow_efficiency'] = {
                'current': flow_eff['avg_flow_efficiency'],
                'waste_time': flow_eff['avg_waste_time']
            }

        return opportunities

    def generate_recommendations(self, opportunities: Dict) -> List[Dict]:
        """Génère des recommandations actionnables avec estimations de gains"""

        print("\n\n💡 GÉNÉRATION DES RECOMMANDATIONS")
        print("=" * 80)

        recommendations = []
        priority_counter = 1

        # Recommandations pour les goulots
        for bn in opportunities.get('bottlenecks', [])[:3]:
            # Estimation des gains
            current_wait = bn['wait_time_mean']
            reduction = 0.40  # Réduction de 40% du temps d'attente

            estimated_wait_reduction = current_wait * reduction
            estimated_wip_reduction = 12 + (bn['impact_pct'] * 0.3)  # Basé sur l'impact
            estimated_leadtime_reduction = 8 + (bn['impact_pct'] * 0.2)

            # Coût estimé basé sur le type d'intervention
            cost = 45000 + np.random.randint(-5000, 15000)  # Coût d'une ressource

            # ROI (gain annuel / coût)
            annual_gain = estimated_wait_reduction * 2000 * 40  # heures * pièces/an * coût/h
            roi = annual_gain / cost if cost > 0 else 0

            rec = {
                'priority': 'HIGH' if priority_counter <= 2 else 'MEDIUM',
                'rank': priority_counter,
                'action': f"Ajouter une ressource au poste '{bn['activity']}'",
                'problem': f"Goulot d'étranglement avec ratio attente/cycle de {bn['wait_to_cycle_ratio']:.2f}",
                'details': f"Cette opération représente {bn['impact_pct']:.1f}% du temps d'attente total. "
                          f"Le temps d'attente moyen est de {bn['wait_time_mean']:.2f}h, "
                          f"soit {bn['wait_to_cycle_ratio']:.1f}x le temps de cycle.",
                'estimated_wip_reduction_pct': estimated_wip_reduction,
                'estimated_leadtime_reduction_pct': estimated_leadtime_reduction,
                'estimated_cost_euros': cost,
                'roi': roi,
                'payback_months': (cost / (annual_gain / 12)) if annual_gain > 0 else 999,
                'implementation_time': '2-4 semaines',
                'type': 'capacity_increase'
            }

            recommendations.append(rec)
            priority_counter += 1

        # Recommandations pour les reworks
        for rw in opportunities.get('high_rework', [])[:2]:
            reduction = 0.35  # Réduction de 35% du taux de rework

            estimated_rework_reduction = rw['rework_rate_pct'] * reduction
            estimated_wip_reduction = 5 + (rw['rework_rate_pct'] * 0.4)
            estimated_leadtime_reduction = 4 + (rw['rework_rate_pct'] * 0.3)

            cost = 15000 + np.random.randint(-3000, 8000)  # Coût formation/procédures

            annual_gain = estimated_rework_reduction * 500 * 40  # rework évités * pièces * coût/h
            roi = annual_gain / cost if cost > 0 else 0

            rec = {
                'priority': 'HIGH' if rw['rework_rate_pct'] > 10 else 'MEDIUM',
                'rank': priority_counter,
                'action': f"Standardiser le contrôle qualité pour '{rw['activity']}'",
                'problem': f"Taux de rework élevé de {rw['rework_rate_pct']:.1f}%",
                'details': f"Sur {rw['total_events']} opérations, {rw['rework_events']} nécessitent un rework. "
                          f"Mise en place de procédures de contrôle en amont et formation des opérateurs.",
                'estimated_wip_reduction_pct': estimated_wip_reduction,
                'estimated_leadtime_reduction_pct': estimated_leadtime_reduction,
                'estimated_cost_euros': cost,
                'roi': roi,
                'payback_months': (cost / (annual_gain / 12)) if annual_gain > 0 else 999,
                'implementation_time': '4-6 semaines',
                'type': 'quality_improvement'
            }

            recommendations.append(rec)
            priority_counter += 1

        # Recommandation pour l'efficacité du flux
        if 'low_flow_efficiency' in opportunities:
            rec = {
                'priority': 'MEDIUM',
                'rank': priority_counter,
                'action': "Réduire les temps d'attente entre opérations",
                'problem': f"Efficacité du flux faible ({opportunities['low_flow_efficiency']['current']:.1f}%)",
                'details': f"En moyenne, {opportunities['low_flow_efficiency']['waste_time']:.2f}h "
                          f"sont perdues par pièce. Optimiser les transitions et la planification.",
                'estimated_wip_reduction_pct': 10,
                'estimated_leadtime_reduction_pct': 15,
                'estimated_cost_euros': 25000,
                'roi': 3.5,
                'payback_months': 4,
                'implementation_time': '6-8 semaines',
                'type': 'process_optimization'
            }

            recommendations.append(rec)
            priority_counter += 1

        # Trier par priorité et impact WIP
        recommendations.sort(key=lambda x: (
            0 if x['priority'] == 'HIGH' else 1,
            -x['estimated_wip_reduction_pct']
        ))

        # Afficher le résumé
        print(f"\n✅ {len(recommendations)} recommandations générées\n")

        for rec in recommendations:
            print(f"🎯 Recommandation #{rec['rank']} [{rec['priority']}]")
            print(f"   Action: {rec['action']}")
            print(f"   Impact WIP: -{rec['estimated_wip_reduction_pct']:.1f}%")
            print(f"   Impact Lead Time: -{rec['estimated_leadtime_reduction_pct']:.1f}%")
            print(f"   Coût: {rec['estimated_cost_euros']:,.0f}€")
            print(f"   ROI: {rec['roi']:.1f}x (payback: {rec['payback_months']:.0f} mois)")
            print()

        return recommendations

    def calculate_optimization_impact(self, recommendations: List[Dict]) -> Dict:
        """Calcule l'impact global des recommandations"""

        print("\n📊 CALCUL DE L'IMPACT GLOBAL")
        print("=" * 80)

        # Impact cumulé (avec effet de saturation)
        total_wip_reduction = 0
        total_leadtime_reduction = 0
        total_cost = 0

        for i, rec in enumerate(recommendations[:3]):  # Top 3 actions
            # Facteur de réduction pour les actions successives (effet décroissant)
            factor = 1.0 / (1 + i * 0.3)

            total_wip_reduction += rec['estimated_wip_reduction_pct'] * factor
            total_leadtime_reduction += rec['estimated_leadtime_reduction_pct'] * factor
            total_cost += rec['estimated_cost_euros']

        # Calcul des nouveaux KPIs
        new_wip = self.baseline_kpis['wip_mean'] * (1 - total_wip_reduction / 100)
        new_leadtime = self.baseline_kpis['lead_time_mean'] * (1 - total_leadtime_reduction / 100)
        new_throughput = self.baseline_kpis['throughput'] * (1 + total_leadtime_reduction / 200)

        impact = {
            'baseline': self.baseline_kpis.copy(),
            'optimized': {
                'lead_time_mean': new_leadtime,
                'wip_mean': new_wip,
                'throughput': new_throughput,
                'rework_rate': self.baseline_kpis['rework_rate'] * 0.7,  # -30%
            },
            'delta': {
                'wip_reduction_pct': total_wip_reduction,
                'leadtime_reduction_pct': total_leadtime_reduction,
                'throughput_increase_pct': total_leadtime_reduction / 2,
                'total_investment_euros': total_cost
            },
            'roi_global': (total_wip_reduction + total_leadtime_reduction) / (total_cost / 10000)
        }

        # Afficher
        print(f"\n📈 Baseline:")
        print(f"   • Lead Time: {self.baseline_kpis['lead_time_mean']:.2f}h")
        print(f"   • WIP moyen: {self.baseline_kpis['wip_mean']:.2f} pièces")
        print(f"   • Débit: {self.baseline_kpis['throughput']:.3f} pièces/h")

        print(f"\n🚀 Après optimisation (Top 3 actions):")
        print(f"   • Lead Time: {new_leadtime:.2f}h ({total_leadtime_reduction:+.1f}%)")
        print(f"   • WIP moyen: {new_wip:.2f} pièces ({total_wip_reduction:+.1f}%)")
        print(f"   • Débit: {new_throughput:.3f} pièces/h (+{total_leadtime_reduction/2:.1f}%)")

        print(f"\n💰 Investissement total: {total_cost:,.0f}€")
        print(f"📊 ROI global: {impact['roi_global']:.1f}x")

        return impact


print("✅ ManufacturingOptimizer class loaded")
