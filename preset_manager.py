# ===============================================
# FICHIER: preset_manager.py (Gestionnaire de presets avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Any, Optional, Tuple, Union

if TYPE_CHECKING:
    from pathlib import Path

import bpy
import json
import os
import numpy as np
from datetime import datetime

from .preferences import get_text

try:
    import sympy as sp
    from sympy import symbols, sympify, lambdify
    from sympy.core.expr import Expr
    from sympy.core.symbol import Symbol
except ImportError:
    sp = None

# Type aliases pour améliorer la lisibilité
PresetData = Dict[str, Any]
PresetCollection = Dict[str, PresetData]
CurveTypePresets = Dict[str, PresetCollection]
ValidationResult = Tuple[bool, str]

class SimplePresetManager:
    """Gestionnaire de presets simplifié et stable avec annotations complètes."""

    def __init__(self) -> None:
        """Initialise le gestionnaire de presets."""
        self.preset_file: str = self.get_preset_file_path()
        self.default_presets: CurveTypePresets = self.get_default_presets()

    def get_preset_file_path(self) -> str:
        """
        Obtient le chemin du fichier de presets utilisateur.

        Returns:
            Chemin vers le fichier JSON des presets
        """
        user_path: Optional[str] = bpy.utils.user_resource('SCRIPTS')
        if not user_path:
            raise RuntimeError("Impossible d'obtenir le répertoire utilisateur Blender")

        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
        return os.path.join(user_path, "curve_presets_simple.json")

    def get_default_presets(self) -> CurveTypePresets:
        """
        Retourne les presets par défaut par type de courbe.

        Returns:
            Dictionnaire des presets organisés par type de courbe
        """
        return {
            "EXPLICIT": {
                "Fonction linéaire": {
                    "equation1": "2*x + 1",
                    "x_min": -5.0, "x_max": 5.0,
                    "resolution": 100,
                    "description": "Droite y = 2x + 1",
                    "category": "Fonctions de base"
                },
                "Parabole": {
                    "equation1": "x**2",
                    "x_min": -5.0, "x_max": 5.0,
                    "resolution": 150,
                    "description": "Parabole y = x²",
                    "category": "Fonctions de base"
                },
                "Sinus": {
                    "equation1": "sin(x)",
                    "x_min": -2*np.pi, "x_max": 2*np.pi,
                    "resolution": 300,
                    "description": "Fonction sinus",
                    "category": "Trigonométrie"
                },
                "Cosinus": {
                    "equation1": "cos(x)",
                    "x_min": -2*np.pi, "x_max": 2*np.pi,
                    "resolution": 300,
                    "description": "Fonction cosinus",
                    "category": "Trigonométrie"
                },
                "Exponentielle": {
                    "equation1": "exp(x)",
                    "x_min": -3.0, "x_max": 2.0,
                    "resolution": 200,
                    "description": "Fonction exponentielle",
                    "category": "Exponentielles"
                },
                "Logarithme": {
                    "equation1": "log(x)",
                    "x_min": 0.1, "x_max": 10.0,
                    "resolution": 200,
                    "description": "Logarithme népérien",
                    "category": "Exponentielles"
                }
            },

            "PARAMETRIC": {
                "Cercle": {
                    "equation1": "cos(t)",
                    "equation2": "sin(t)",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 200,
                    "description": "Cercle unité",
                    "category": "Courbes fermées"
                },
                "Ellipse": {
                    "equation1": "3*cos(t)",
                    "equation2": "2*sin(t)",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 200,
                    "description": "Ellipse 3x2",
                    "category": "Courbes fermées"
                },
                "Spirale d'Archimède": {
                    "equation1": "t*cos(t)",
                    "equation2": "t*sin(t)",
                    "t_min": 0.0, "t_max": 6*np.pi,
                    "resolution": 500,
                    "description": "Spirale à espacement constant",
                    "category": "Spirales"
                },
                "Épicycloïde": {
                    "equation1": "3*cos(t) + cos(3*t)",
                    "equation2": "3*sin(t) - sin(3*t)",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 300,
                    "description": "Épicycloïde à 4 boucles",
                    "category": "Cycloïdes"
                }
            },

            "POLAR": {
                "Cercle polaire": {
                    "equation1": "2",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 150,
                    "description": "Cercle de rayon 2",
                    "category": "Courbes de base"
                },
                "Cardioïde": {
                    "equation1": "1 + cos(theta)",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 300,
                    "description": "Courbe en cœur",
                    "category": "Limaçons"
                },
                "Rose 4 pétales": {
                    "equation1": "cos(2*theta)",
                    "t_min": 0.0, "t_max": 2*np.pi,
                    "resolution": 300,
                    "description": "Rose à 4 pétales",
                    "category": "Roses"
                },
                "Spirale logarithmique": {
                    "equation1": "exp(0.2*theta)",
                    "t_min": 0.0, "t_max": 4*np.pi,
                    "resolution": 400,
                    "description": "Spirale exponentielle",
                    "category": "Spirales"
                }
            },

            "IMPLICIT": {
                "Cercle": {
                    "equation1": "x**2 + y**2 - 4",
                    "x_min": -3.0, "x_max": 3.0,
                    "y_min": -3.0, "y_max": 3.0,
                    "resolution": 200,
                    "description": "Cercle de rayon 2",
                    "category": "Coniques"
                },
                "Ellipse": {
                    "equation1": "x**2/9 + y**2/4 - 1",
                    "x_min": -4.0, "x_max": 4.0,
                    "y_min": -3.0, "y_max": 3.0,
                    "resolution": 200,
                    "description": "Ellipse 3x2",
                    "category": "Coniques"
                },
                "Lemniscate": {
                    "equation1": "(x**2 + y**2)**2 - 2*(x**2 - y**2)",
                    "x_min": -2.0, "x_max": 2.0,
                    "y_min": -1.5, "y_max": 1.5,
                    "resolution": 300,
                    "description": "Courbe en huit",
                    "category": "Courbes spéciales"
                }
            }
        }

    def load_user_presets(self) -> CurveTypePresets:
        """
        Charge les presets utilisateur depuis le fichier JSON.

        Returns:
            Dictionnaire des presets utilisateur ou dictionnaire vide si erreur
        """
        try:
            if os.path.exists(self.preset_file):
                with open(self.preset_file, 'r', encoding='utf-8') as f:
                    data: Dict[str, Any] = json.load(f)
                    return data.get('presets', {})
            return {}
        except Exception as e:
            print(f"Erreur chargement presets: {e}")
            return {}

    def save_user_presets(self, user_presets: CurveTypePresets) -> bool:
        """
        Sauvegarde les presets utilisateur dans le fichier JSON.

        Args:
            user_presets: Dictionary des presets à sauvegarder

        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            data: Dict[str, Any] = {
                'presets': user_presets,
                'last_modified': datetime.now().isoformat(),
                'version': '4.3'
            }

            with open(self.preset_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False

    def get_all_presets(self, curve_type: str) -> PresetCollection:
        """
        Retourne tous les presets (par défaut + utilisateur) pour un type donné.

        Args:
            curve_type: Type de courbe ('EXPLICIT', 'PARAMETRIC', etc.)

        Returns:
            Dictionnaire de tous les presets avec métadonnées
        """
        presets: PresetCollection = {}

        # Presets par défaut
        if curve_type in self.default_presets:
            for name, data in self.default_presets[curve_type].items():
                presets[name] = {**data, 'source': 'default', 'editable': False}

        # Presets utilisateur
        user_presets: CurveTypePresets = self.load_user_presets()
        if curve_type in user_presets:
            for name, data in user_presets[curve_type].items():
                presets[name] = {**data, 'source': 'user', 'editable': True}

        return presets

    def get_preset_names(self, curve_type: str) -> List[str]:
        """
        Retourne la liste des noms de presets pour un type donné.

        Args:
            curve_type: Type de courbe

        Returns:
            Liste des noms de presets
        """
        all_presets: PresetCollection = self.get_all_presets(curve_type)
        return list(all_presets.keys())

    def get_preset_by_name(self, curve_type: str, name: str) -> Optional[PresetData]:
        """
        Récupère un preset par son nom et type de courbe.

        Args:
            curve_type: Type de courbe
            name: Nom du preset

        Returns:
            Données du preset ou None si non trouvé
        """
        all_presets: PresetCollection = self.get_all_presets(curve_type)
        return all_presets.get(name)

    def validate_preset_data(self, curve_type: str, data: PresetData) -> ValidationResult:
        """
        Valide les données d'un preset selon son type.

        Args:
            curve_type: Type de courbe
            data: Données du preset à valider

        Returns:
            Tuple (validité, message d'erreur)
        """
        required_fields: Dict[str, List[str]] = {
            'EXPLICIT': ['equation1', 'x_min', 'x_max'],
            'PARAMETRIC': ['equation1', 'equation2', 't_min', 't_max'],
            'POLAR': ['equation1', 't_min', 't_max'],
            'IMPLICIT': ['equation1', 'x_min', 'x_max', 'y_min', 'y_max']
        }

        if curve_type not in required_fields:
            return False, f"Type de courbe '{curve_type}' non supporté"

        for field in required_fields[curve_type]:
            if field not in data:
                return False, f"Champ requis manquant: {field}"

        # Validation avec SymPy si disponible
        if sp is not None:
            try:
                if curve_type == 'EXPLICIT':
                    x: Symbol = sp.symbols('x')
                    expr: Expr = sp.sympify(data['equation1'])
                    if x not in expr.free_symbols:
                        return False, "L'équation doit contenir 'x'"

                elif curve_type == 'PARAMETRIC':
                    t: Symbol = sp.symbols('t')
                    expr1: Expr = sp.sympify(data['equation1'])
                    expr2: Expr = sp.sympify(data['equation2'])
                    if t not in expr1.free_symbols or t not in expr2.free_symbols:
                        return False, "Les équations doivent contenir 't'"

                elif curve_type == 'POLAR':
                    theta: Symbol = sp.symbols('theta')
                    expr = sp.sympify(data['equation1'])
                    if theta not in expr.free_symbols:
                        return False, "L'équation doit contenir 'theta'"

                elif curve_type == 'IMPLICIT':
                    x, y = sp.symbols('x y')
                    expr = sp.sympify(data['equation1'])
                    if not (x in expr.free_symbols or y in expr.free_symbols):
                        return False, "L'équation doit contenir 'x' et/ou 'y'"

            except Exception as e:
                return False, f"Erreur de syntaxe: {str(e)[:50]}"

        return True, "Preset valide"

    def create_preset(self, curve_type: str, name: str, data: PresetData) -> ValidationResult:
        """
        Crée un nouveau preset utilisateur.

        Args:
            curve_type: Type de courbe
            name: Nom du preset
            data: Données du preset

        Returns:
            Tuple (succès, message)
        """
        # Validation
        valid, message = self.validate_preset_data(curve_type, data)
        if not valid:
            return False, message

        # Charger presets existants
        user_presets: CurveTypePresets = self.load_user_presets()

        # Vérifier que le nom n'existe pas
        if curve_type in user_presets and name in user_presets[curve_type]:
            return False, get_text('preset_exists')

        # Créer la structure si nécessaire
        if curve_type not in user_presets:
            user_presets[curve_type] = {}

        # Ajouter métadonnées
        preset_data: PresetData = {
            **data,
            'created_date': datetime.now().isoformat(),
            'author': 'Utilisateur'
        }

        user_presets[curve_type][name] = preset_data

        # Sauvegarder
        if self.save_user_presets(user_presets):
            return True, f"{get_text('preset_created')}: '{name}'"
        else:
            return False, get_text('save_error')

    def delete_preset(self, curve_type: str, name: str) -> ValidationResult:
        """
        Supprime un preset utilisateur.

        Args:
            curve_type: Type de courbe
            name: Nom du preset à supprimer

        Returns:
            Tuple (succès, message)
        """
        user_presets: CurveTypePresets = self.load_user_presets()

        if curve_type not in user_presets or name not in user_presets[curve_type]:
            return False, f"{get_text('preset_not_found')}: '{name}'"

        del user_presets[curve_type][name]

        # Nettoyer si vide
        if not user_presets[curve_type]:
            del user_presets[curve_type]

        if self.save_user_presets(user_presets):
            return True, f"{get_text('preset_deleted')}: '{name}'"
        else:
            return False, get_text('save_error')

# ===============================================
# CONTINUATION DANS LE PROCHAIN MESSAGE...
# ===============================================
