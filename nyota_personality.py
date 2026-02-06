import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List


# ============================================
# CONFIGURATION DES 8 AXES NYOTA
# ============================================

AXES_CONFIG = {
    "Ouverture & Curiosité": {
        "bloc1": list(range(1, 7)),      # Q1-6
        "bloc2": [14],                    # Q14
        "bloc3": [3, 6],                  # Q3, Q6
        "invert": []
    },
    
    "Discipline & Fiabilité": {
        "bloc1": list(range(7, 13)),     # Q7-12
        "bloc3": [7, 11, 12],             # Q7, Q11, Q12
        "invert": []
    },
    
    "Influence & Présence": {
        "bloc1": list(range(13, 19)),    # Q13-18
        "bloc2": [15],                    # Q15
        "invert": []
    },
    
    "Coopération": {
        "bloc1": list(range(19, 25)),    # Q19-24
        "bloc2": [16],                    # Q16
        "invert": []
    },
    
    "Résilience & Stress": {
        "bloc1": list(range(25, 31)),    # Q25-30
        "bloc2": list(range(1, 9)),      # Q1-8 (inversés)
        "invert": [("bloc2", q) for q in range(1, 9)]
    },
    
    "Drive & Motivation": {
        "bloc2": [9, 10, 11, 12, 13, 15, 16],  # Q9-13, 15, 16
        "invert": []
    },
    
    "Style d'action": {
        "bloc3": list(range(1, 13)),     # Q1-12
        "invert": []
    },
    
    "Alignement stratégique": {
        "bloc4": list(range(1, 15)),     # Q1-14
        "invert": []
    }
}


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def invert_score(value: int) -> int:
    """Inverse un item à risque (1→5, 5→1)"""
    return 6 - value


def normalize_to_100(score: float) -> float:
    """Normalise une moyenne 1-5 vers 0-100"""
    return round(((score - 1) / 4) * 100, 2)


# ============================================
# CONVERSION JSON → STRUCTURE PAR BLOCS
# ============================================

def parse_responses(json_data: Dict[int, int]) -> Dict[str, Dict[int, int]]:
    """
    Convertit les réponses JSON plates en structure par blocs.
    
    JSON attendu : {1: 4, 2: 3, ...}  (numérotation globale 1-72)
    
    Retourne : {
        "bloc1": {1: 4, 2: 3, ...},
        "bloc2": {1: 5, 2: 2, ...},
        ...
    }
    """
    responses = {
        "bloc1": {},
        "bloc2": {},
        "bloc3": {},
        "bloc4": {}
    }
    
    # Bloc 1 : items 1-30
    for i in range(1, 31):
        if i in json_data:
            responses["bloc1"][i] = json_data[i]
    
    # Bloc 2 : items 31-46
    for i in range(31, 47):
        if i in json_data:
            responses["bloc2"][i - 30] = json_data[i]
    
    # Bloc 3 : items 47-58
    for i in range(47, 59):
        if i in json_data:
            responses["bloc3"][i - 46] = json_data[i]
    
    # Bloc 4 : items 59-72
    for i in range(59, 73):
        if i in json_data:
            responses["bloc4"][i - 58] = json_data[i]
    
    return responses


# ============================================
# CALCUL DES SCORES PAR AXE
# ============================================

def compute_axis_score(axis_name: str, config: dict, responses: dict) -> float:
    """Calcule le score d'un axe en agrégeant les items configurés"""
    
    values = []
    
    # Parcourir tous les blocs configurés pour cet axe
    for bloc_name in ["bloc1", "bloc2", "bloc3", "bloc4"]:
        if bloc_name not in config:
            continue
        
        for item_num in config[bloc_name]:
            if item_num not in responses[bloc_name]:
                raise ValueError(f"❌ [{axis_name}] Item manquant : {bloc_name} Q{item_num}")
            
            value = responses[bloc_name][item_num]
            
            # Vérifier si l'item doit être inversé
            if (bloc_name, item_num) in config["invert"]:
                value = invert_score(value)
            
            values.append(value)
    
    # Moyenne puis normalisation
    if not values:
        return 0.0
    
    mean_score = sum(values) / len(values)
    return normalize_to_100(mean_score)


def compute_all_scores(json_responses: Dict[int, int]) -> Dict[str, float]:
    """Calcule les 8 scores NYOTA"""
    
    responses = parse_responses(json_responses)
    scores = {}
    
    for axis_name, config in AXES_CONFIG.items():
        scores[axis_name] = compute_axis_score(axis_name, config, responses)
    
    return scores


# ============================================
# VISUALISATION KIVIAT (RADAR)
# ============================================

def plot_kiviat(scores: Dict[str, float], save_path: str = None):
    """Génère le diagramme radar à 8 axes"""
    
    if len(scores) != 8:
        raise ValueError(f"⚠️ Le diagramme nécessite 8 axes, trouvé : {len(scores)}")
    
    labels = list(scores.keys())
    values = list(scores.values())
    
    # Calcul des angles (8 axes)
    num_axes = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_axes, endpoint=False).tolist()
    
    # Fermeture du polygone
    values += values[:1]
    angles += angles[:1]
    
    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Configuration des axes
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # Labels des axes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
    
    # Échelle 0-100
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, color='gray')
    
    # Tracé du profil
    ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB', label='Profil')
    ax.fill(angles, values, alpha=0.25, color='#2E86AB')
    
    # Grille
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Titre
    ax.set_title("NYOTA Personality – Profil à 8 dimensions", 
                 pad=30, fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Diagramme sauvegardé : {save_path}")
    
    plt.show()


# ============================================
# FONCTION PRINCIPALE
# ============================================

def generate_nyota_report(json_file: str, save_diagram: str = None):
    """
    Génère le rapport NYOTA complet à partir d'un fichier JSON.
    
    Args:
        json_file: Chemin vers le JSON des réponses
        save_diagram: Optionnel - chemin pour sauvegarder le diagramme
    """
    
    print("=" * 60)
    print("🔍 NYOTA PERSONALITY - ANALYSE EN COURS")
    print("=" * 60)
    
    # Chargement des réponses
    with open(json_file, 'r', encoding='utf-8') as f:
        responses = json.load(f)
    
    # Conversion des clés en entiers
    responses = {int(k): v for k, v in responses.items()}
    
    print(f"✅ {len(responses)} réponses chargées")
    
    # Calcul des scores
    scores = compute_all_scores(responses)
    
    # Affichage des résultats
    print("\n📊 SCORES PAR AXE (sur 100)")
    print("-" * 60)
    for axis, score in scores.items():
        bar = "█" * int(score / 5)
        print(f"{axis:.<40} {score:>6.2f} {bar}")
    
    print("\n" + "=" * 60)
    
    # Génération du diagramme
    plot_kiviat(scores, save_diagram)
    
    return scores


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    
    # Test avec ton fichier
    scores = generate_nyota_report(
        json_file="reponse_per1.json",
        save_diagram="nyota_profile.png"  # Optionnel
    )
