import json
import numpy as np
from typing import Dict, List

AXES_CONFIG = {
    "Ouverture & Curiosité": {
        "bloc1": list(range(1, 7)),
        "bloc2": [14],
        "bloc3": [3, 6],
        "invert": []
    },
    "Discipline & Fiabilité": {
        "bloc1": list(range(7, 13)),
        "bloc3": [7, 11, 12],
        "invert": []
    },
    "Influence & Présence": {
        "bloc1": list(range(13, 19)),
        "bloc2": [15],
        "invert": []
    },
    "Coopération": {
        "bloc1": list(range(19, 25)),
        "bloc2": [16],
        "invert": []
    },
    "Résilience & Stress": {
        "bloc1": list(range(25, 31)),
        "bloc2": list(range(1, 9)),
        "invert": [("bloc2", q) for q in range(1, 9)]
    },
    "Drive & Motivation": {
        "bloc2": [9, 10, 11, 12, 13, 15, 16],
        "invert": []
    },
    "Style d'action": {
        "bloc3": list(range(1, 13)),
        "invert": []
    },
    "Alignement stratégique": {
        "bloc4": list(range(1, 15)),
        "invert": []
    }
}

def invert_score(value: int) -> int:
    return 6 - value

def normalize_to_100(score: float) -> float:
    return round(((score - 1) / 4) * 100, 2)

def parse_responses(json_data: Dict[int, int]) -> Dict[str, Dict[int, int]]:
    responses = {
        "bloc1": {},
        "bloc2": {},
        "bloc3": {},
        "bloc4": {}
    }
    
    for i in range(1, 31):
        if i in json_data:
            responses["bloc1"][i] = json_data[i]
    
    for i in range(31, 47):
        if i in json_data:
            responses["bloc2"][i - 30] = json_data[i]
    
    for i in range(47, 59):
        if i in json_data:
            responses["bloc3"][i - 46] = json_data[i]
    
    for i in range(59, 73):
        if i in json_data:
            responses["bloc4"][i - 58] = json_data[i]
    
    return responses

def compute_axis_score(axis_name: str, config: dict, responses: dict) -> float:
    values = []
    
    for bloc_name in ["bloc1", "bloc2", "bloc3", "bloc4"]:
        if bloc_name not in config:
            continue
        
        for item_num in config[bloc_name]:
            if item_num not in responses[bloc_name]:
                continue
            
            value = responses[bloc_name][item_num]
            
            if (bloc_name, item_num) in config["invert"]:
                value = invert_score(value)
            
            values.append(value)
    
    if not values:
        return 0.0
    
    mean_score = sum(values) / len(values)
    return normalize_to_100(mean_score)

def compute_all_scores(json_responses: Dict[int, int]) -> Dict[str, float]:
    responses = parse_responses(json_responses)
    scores = {}
    
    for axis_name, config in AXES_CONFIG.items():
        scores[axis_name] = compute_axis_score(axis_name, config, responses)
    
    return scores

def generate_radar_chart_data(scores: Dict[str, float]):
    """Prépare les données pour le diagramme radar en format JSON"""
    labels = list(scores.keys())
    values = list(scores.values())
    
    return {
        "labels": labels,
        "datasets": [{
            "label": "Score NYOTA",
            "data": values,
            "backgroundColor": "rgba(46, 134, 171, 0.2)",
            "borderColor": "rgba(46, 134, 171, 1)",
            "pointBackgroundColor": "rgba(46, 134, 171, 1)",
            "pointBorderColor": "#fff",
            "pointHoverBackgroundColor": "#fff",
            "pointHoverBorderColor": "rgba(46, 134, 171, 1)"
        }]
    }