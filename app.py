from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import io
from nyota_calculator import compute_all_scores, generate_radar_chart_data
import matplotlib.pyplot as plt
import numpy as np
import base64

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes depuis ton frontend

@app.route('/api/calculate', methods=['POST'])
def calculate_scores():
    try:
        data = request.json
        responses = {int(k): int(v) for k, v in data.items()}
        
        scores = compute_all_scores(responses)
        chart_data = generate_radar_chart_data(scores)
        
        return jsonify({
            "success": True,
            "scores": scores,
            "chart_data": chart_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        scores = data.get('scores', {})
        
        # Créer le diagramme radar
        labels = list(scores.keys())
        values = list(scores.values())
        
        num_axes = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_axes, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, polar=True)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 100)
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_title("NYOTA Personality - Profil à 8 dimensions", pad=20)
        
        # Convertir en image base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            "success": True,
            "image": img_str
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)