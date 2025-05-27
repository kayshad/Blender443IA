bl_info = {
    "name": "Courbes du Plan - Presets Fixes",
    "description": "Système stable de gestion de presets pour courbes mathématiques",
    "author": "TonNom + Assistant",
    "version": (4, 2),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > Courbes du Plan",
    "category": "Add Curve"
}

import bpy
import json
import os
import numpy as np
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    sp = None
    SYMPY_AVAILABLE = False

# ============ SYSTÈME DE TRADUCTION ============

TRANSLATIONS = {
    'fr': {
        # Types de courbes
        'curve_type': "Type de courbe",
        'explicit': "Explicite (y=f(x))",
        'parametric': "Paramétrique (x(t),y(t))",
        'polar': "Polaire (r=f(θ))",
        'implicit': "Implicite (F(x,y)=0)",
        'explicit_desc': "Fonction explicite",
        'parametric_desc': "Courbe paramétrique",
        'polar_desc': "Coordonnées polaires",
        'implicit_desc': "Équation implicite",
        
        # Interface principale
        'equations': "Équations:",
        'parameters': "Paramètres:",
        'validation': "Validation:",
        'resolution': "Résolution",
        'generate_curve': "Générer courbe",
        'validate': "Valider",
        
        # Presets
        'presets': "Presets",
        'navigation': "Navigation:",
        'select_preset': "-- Sélectionner un preset --",
        'no_preset': "Aucun preset sélectionné",
        'refresh': "Actualiser",
        'create_preset': "Créer preset:",
        'preset_name': "Nom du preset",
        'description': "Description",
        'no_presets': "Aucun preset disponible",
        'details': "Détails:",
        'source': "Source:",
        'default_source': "Par défaut",
        'user_source': "Utilisateur",
        'equation': "Équation:",
        
        # Messages
        'valid_params': "Paramètres valides ✓",
        'validation_failed': "Validation échouée",
        'no_preset_selected': "Aucun preset sélectionné",
        'preset_not_found': "Preset introuvable",
        'preset_loaded': "Preset chargé",
        'preset_created': "Preset créé",
        'preset_deleted': "Preset supprimé",
        'cannot_delete': "Ce preset ne peut pas être supprimé",
        'preset_exists': "Un preset avec ce nom existe déjà",
        'save_error': "Erreur de sauvegarde",
        'name_required': "Nom du preset requis",
        'not_enough_points': "Pas assez de points valides",
        'no_curve_detected': "Pas de courbe détectée",
        'sympy_not_installed': "SymPy non installé !",
        
        # Préférences
        'preferences': "Préférences",
        'language': "Langue",
        'french': "Français",
        'english': "English",
        'sympy_management': "Gestion de SymPy",
        'sympy_status': "Statut de SymPy:",
        'sympy_installed': "SymPy est installé",
        'sympy_not_installed_pref': "SymPy n'est pas installé",
        'install_sympy': "Installer SymPy",
        'installing_sympy': "Installation de SymPy en cours...",
        'sympy_install_success': "SymPy installé avec succès !",
        'sympy_install_error': "Erreur lors de l'installation de SymPy",
        'restart_blender': "Redémarrez Blender pour prendre en compte les changements",
        'check_sympy': "Vérifier SymPy",
        'sympy_required': "SymPy est requis pour ce addon. Installez-le dans les préférences.",
    },
    
    'en': {
        # Curve types
        'curve_type': "Curve Type",
        'explicit': "Explicit (y=f(x))",
        'parametric': "Parametric (x(t),y(t))",
        'polar': "Polar (r=f(θ))",
        'implicit': "Implicit (F(x,y)=0)",
        'explicit_desc': "Explicit function",
        'parametric_desc': "Parametric curve",
        'polar_desc': "Polar coordinates",
        'implicit_desc': "Implicit equation",
        
        # Main interface
        'equations': "Equations:",
        'parameters': "Parameters:",
        'validation': "Validation:",
        'resolution': "Resolution",
        'generate_curve': "Generate Curve",
        'validate': "Validate",
        
        # Presets
        'presets': "Presets",
        'navigation': "Navigation:",
        'select_preset': "-- Select a preset --",
        'no_preset': "No preset selected",
        'refresh': "Refresh",
        'create_preset': "Create preset:",
        'preset_name': "Preset name",
        'description': "Description",
        'no_presets': "No presets available",
        'details': "Details:",
        'source': "Source:",
        'default_source': "Default",
        'user_source': "User",
        'equation': "Equation:",
        
        # Messages
        'valid_params': "Valid parameters ✓",
        'validation_failed': "Validation failed",
        'no_preset_selected': "No preset selected",
        'preset_not_found': "Preset not found",
        'preset_loaded': "Preset loaded",
        'preset_created': "Preset created",
        'preset_deleted': "Preset deleted",
        'cannot_delete': "This preset cannot be deleted",
        'preset_exists': "A preset with this name already exists",
        'save_error': "Save error",
        'name_required': "Preset name required",
        'not_enough_points': "Not enough valid points",
        'no_curve_detected': "No curve detected",
        'sympy_not_installed': "SymPy not installed!",
        
        # Preferences
        'preferences': "Preferences",
        'language': "Language",
        'french': "Français",
        'english': "English",
        'sympy_management': "SymPy Management",
        'sympy_status': "SymPy Status:",
        'sympy_installed': "SymPy is installed",
        'sympy_not_installed_pref': "SymPy is not installed",
        'install_sympy': "Install SymPy",
        'installing_sympy': "Installing SymPy...",
        'sympy_install_success': "SymPy installed successfully!",
        'sympy_install_error': "Error installing SymPy",
        'restart_blender': "Restart Blender to apply changes",
        'check_sympy': "Check SymPy",
        'sympy_required': "SymPy is required for this addon. Install it in preferences.",
    }
}

def get_addon_preferences():
    """Récupère les préférences de l'addon de manière sécurisée"""
    try:
        # Déterminer le nom de l'addon
        addon_name = __name__.split('.')[0] if '.' in __name__ else __name__
        # Accéder aux préférences
        return bpy.context.preferences.addons[addon_name].preferences
    except (KeyError, AttributeError):
        return None

def get_text(key: str) -> str:
    """Récupère le texte traduit selon la langue sélectionnée"""
    try:
        prefs = get_addon_preferences()
        if prefs and hasattr(prefs, 'language'):
            lang = prefs.language
            return TRANSLATIONS.get(lang, TRANSLATIONS['fr']).get(key, key)
    except Exception:
        pass
    # Fallback vers français si erreur
    return TRANSLATIONS['fr'].get(key, key)

# ============ PRÉFÉRENCES DE L'ADDON ============

class PLAN_CURVES_AddonPreferences(bpy.types.AddonPreferences):
    """Préférences de l'addon"""
    # Utiliser __name__ pour un addon monofichier, __package__ pour un addon multi-fichiers
    bl_idname = __name__.split('.')[0] if '.' in __name__ else __name__

    # === LANGUE ===
    language: bpy.props.EnumProperty(
        name="Language",
        items=[
            ('fr', "Français", "Interface en français"),
            ('en', "English", "English interface"),
        ],
        default='fr',
        description="Langue de l'interface"
    )

    # === SYMPY ===
    sympy_check_done: bpy.props.BoolProperty(
        name="SymPy Check Done",
        default=False,
        description="Indique si la vérification SymPy a été faite"
    )

    sympy_install_status: bpy.props.StringProperty(
        name="SymPy Install Status",
        default="",
        description="Statut de l'installation SymPy"
    )

    def draw(self, context):
        layout = self.layout
        
        # === SECTION LANGUE ===
        lang_box = layout.box()
        lang_box.label(text=get_text('language'), icon='WORLD')
        lang_box.prop(self, "language", expand=True)
        
        layout.separator()
        
        # === SECTION SYMPY ===
        sympy_box = layout.box()
        sympy_box.label(text=get_text('sympy_management'), icon='CONSOLE')
        
        # Statut SymPy
        status_row = sympy_box.row()
        status_row.label(text=get_text('sympy_status'))
        
        if SYMPY_AVAILABLE:
            status_row.label(text=get_text('sympy_installed'), icon='CHECKMARK')
        else:
            status_row.label(text=get_text('sympy_not_installed_pref'), icon='ERROR')
        
        # Boutons
        buttons_row = sympy_box.row(align=True)
        buttons_row.operator("plan_curves.check_sympy", 
                           text=get_text('check_sympy'), 
                           icon='FILE_REFRESH')
        
        if not SYMPY_AVAILABLE:
            buttons_row.operator("plan_curves.install_sympy", 
                               text=get_text('install_sympy'), 
                               icon='IMPORT')
        
        # Messages de statut
        if self.sympy_install_status:
            msg_box = sympy_box.box()
            if "success" in self.sympy_install_status.lower() or "succès" in self.sympy_install_status.lower():
                msg_box.label(text=self.sympy_install_status, icon='CHECKMARK')
                msg_box.label(text=get_text('restart_blender'), icon='INFO')
            elif "error" in self.sympy_install_status.lower() or "erreur" in self.sympy_install_status.lower():
                msg_box.label(text=self.sympy_install_status, icon='ERROR')
            else:
                msg_box.label(text=self.sympy_install_status, icon='INFO')
        
        layout.separator()
        
        # === INFORMATIONS ===
        info_box = layout.box()
        info_box.label(text="Informations", icon='INFO')
        info_box.label(text=f"Version: {bl_info['version']}")
        info_box.label(text=f"Auteur: {bl_info['author']}")

# ============ OPÉRATEURS POUR SYMPY ============

class PLAN_CURVES_OT_check_sympy(bpy.types.Operator):
    """Vérifie le statut de SymPy"""
    bl_idname = "plan_curves.check_sympy"
    bl_label = "Check SymPy"
    bl_description = "Vérifie si SymPy est installé"

    def execute(self, context):
        global SYMPY_AVAILABLE, sp
        
        # Réimporter pour vérifier
        try:
            import importlib
            if sp is not None:
                importlib.reload(sp)
            else:
                import sympy as sp
            SYMPY_AVAILABLE = True
            
            prefs = get_addon_preferences()
            if prefs:
                prefs.sympy_install_status = get_text('sympy_installed')
            
            self.report({'INFO'}, get_text('sympy_installed'))
            
        except ImportError:
            SYMPY_AVAILABLE = False
            sp = None
            
            prefs = get_addon_preferences()
            if prefs:
                prefs.sympy_install_status = get_text('sympy_not_installed_pref')
            
            self.report({'WARNING'}, get_text('sympy_not_installed_pref'))
        
        return {'FINISHED'}

class PLAN_CURVES_OT_install_sympy(bpy.types.Operator):
    """Installe SymPy via pip"""
    bl_idname = "plan_curves.install_sympy"
    bl_label = "Install SymPy"
    bl_description = "Installe SymPy automatiquement"

    def execute(self, context):
        prefs = get_addon_preferences()
        if prefs:
            prefs.sympy_install_status = get_text('installing_sympy')
        
        try:
            # Obtenir le chemin de l'exécutable Python de Blender
            python_exe = sys.executable
            
            # Installer SymPy
            result = subprocess.run([
                python_exe, "-m", "pip", "install", "sympy"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Installation réussie
                if prefs:
                    prefs.sympy_install_status = get_text('sympy_install_success')
                self.report({'INFO'}, get_text('sympy_install_success'))
                
                # Essayer de réimporter
                bpy.ops.plan_curves.check_sympy()
                
            else:
                # Erreur d'installation
                error_msg = f"{get_text('sympy_install_error')}: {result.stderr}"
                if prefs:
                    prefs.sympy_install_status = error_msg[:100]
                self.report({'ERROR'}, error_msg)
                
        except subprocess.TimeoutExpired:
            error_msg = f"{get_text('sympy_install_error')}: Timeout"
            if prefs:
                prefs.sympy_install_status = error_msg
            self.report({'ERROR'}, error_msg)
            
        except Exception as e:
            error_msg = f"{get_text('sympy_install_error')}: {str(e)}"
            if prefs:
                prefs.sympy_install_status = error_msg[:100]
            self.report({'ERROR'}, error_msg)
        
        return {'FINISHED'}

# ============ GESTIONNAIRE DE PRESETS SIMPLIFIÉ ============

class SimplePresetManager:
    """Gestionnaire de presets simplifié et stable"""

    def __init__(self):
        self.preset_file = self.get_preset_file_path()
        self.default_presets = self.get_default_presets()

    def get_preset_file_path(self):
        user_path = bpy.utils.user_resource('SCRIPTS')
        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
        return os.path.join(user_path, "curve_presets_simple.json")

    def get_default_presets(self) -> Dict[str, Dict[str, Any]]:
        """Presets par défaut par type de courbe"""
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

    def load_user_presets(self) -> Dict[str, Dict[str, Any]]:
        """Charge les presets utilisateur"""
        try:
            if os.path.exists(self.preset_file):
                with open(self.preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('presets', {})
            return {}
        except Exception as e:
            print(f"Erreur chargement presets: {e}")
            return {}

    def save_user_presets(self, user_presets: Dict[str, Dict[str, Any]]) -> bool:
        """Sauvegarde les presets utilisateur"""
        try:
            data = {
                'presets': user_presets,
                'last_modified': datetime.now().isoformat(),
                'version': '4.2'
            }

            with open(self.preset_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False

    def get_all_presets(self, curve_type: str) -> Dict[str, Any]:
        """Retourne tous les presets pour un type donné"""
        presets = {}

        # Presets par défaut
        if curve_type in self.default_presets:
            for name, data in self.default_presets[curve_type].items():
                presets[name] = {**data, 'source': 'default', 'editable': False}

        # Presets utilisateur
        user_presets = self.load_user_presets()
        if curve_type in user_presets:
            for name, data in user_presets[curve_type].items():
                presets[name] = {**data, 'source': 'user', 'editable': True}

        return presets

    def get_preset_names(self, curve_type: str) -> List[str]:
        """Retourne la liste des noms de presets"""
        all_presets = self.get_all_presets(curve_type)
        return list(all_presets.keys())

    def get_preset_by_name(self, curve_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un preset par son nom"""
        all_presets = self.get_all_presets(curve_type)
        return all_presets.get(name)

    def validate_preset_data(self, curve_type: str, data: Dict[str, Any]) -> tuple[bool, str]:
        """Valide les données d'un preset"""
        required_fields = {
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
                    x = sp.symbols('x')
                    expr = sp.sympify(data['equation1'])
                    if x not in expr.free_symbols:
                        return False, "L'équation doit contenir 'x'"

                elif curve_type == 'PARAMETRIC':
                    t = sp.symbols('t')
                    expr1 = sp.sympify(data['equation1'])
                    expr2 = sp.sympify(data['equation2'])
                    if t not in expr1.free_symbols or t not in expr2.free_symbols:
                        return False, "Les équations doivent contenir 't'"

                elif curve_type == 'POLAR':
                    theta = sp.symbols('theta')
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

    def create_preset(self, curve_type: str, name: str, data: Dict[str, Any]) -> tuple[bool, str]:
        """Crée un nouveau preset"""
        # Validation
        valid, message = self.validate_preset_data(curve_type, data)
        if not valid:
            return False, message

        # Charger presets existants
        user_presets = self.load_user_presets()

        # Vérifier que le nom n'existe pas
        if curve_type in user_presets and name in user_presets[curve_type]:
            return False, get_text('preset_exists')

        # Créer la structure si nécessaire
        if curve_type not in user_presets:
            user_presets[curve_type] = {}

        # Ajouter métadonnées
        preset_data = {
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

    def delete_preset(self, curve_type: str, name: str) -> tuple[bool, str]:
        """Supprime un preset utilisateur"""
        user_presets = self.load_user_presets()

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

# ============ FONCTIONS POUR LES ENUM PROPERTIES ============

def get_preset_enum_items(self, context):
    """Items pour le menu des presets - Version sécurisée"""
    try:
        # Obtenir le type de courbe actuel
        curve_type = getattr(self, 'curve_type', 'EXPLICIT')

        manager = SimplePresetManager()
        preset_names = manager.get_preset_names(curve_type)

        items = [('NONE', get_text('select_preset'), get_text('no_preset'))]

        for name in preset_names:
            preset_data = manager.get_preset_by_name(curve_type, name)
            if preset_data:
                desc = preset_data.get('description', 'Pas de description')
                items.append((name, name, desc))

        return items

    except Exception as e:
        print(f"Erreur get_preset_enum_items: {e}")
        return [('NONE', 'Erreur', 'Erreur de chargement')]

# ============ PROPRIÉTÉS PRINCIPALES SIMPLIFIÉES ============

class PlanCurvesProperties(bpy.types.PropertyGroup):
    """Propriétés principales simplifiées"""

    # === PROPRIÉTÉS DE BASE ===
    curve_type: bpy.props.EnumProperty(
        name="Type de courbe",
        items=[
            ('EXPLICIT', "Explicite (y=f(x))", "Fonction explicite"),
            ('PARAMETRIC', "Paramétrique (x(t),y(t))", "Courbe paramétrique"),
            ('POLAR', "Polaire (r=f(θ))", "Coordonnées polaires"),
            ('IMPLICIT', "Implicite (F(x,y)=0)", "Équation implicite"),
        ],
        default='EXPLICIT'
    )

    equation1: bpy.props.StringProperty(name="Équation 1", default="x**2")
    equation2: bpy.props.StringProperty(name="Équation 2", default="t")

    x_min: bpy.props.FloatProperty(name="x min", default=-5.0)
    x_max: bpy.props.FloatProperty(name="x max", default=5.0)
    y_min: bpy.props.FloatProperty(name="y min", default=-5.0)
    y_max: bpy.props.FloatProperty(name="y max", default=5.0)
    t_min: bpy.props.FloatProperty(name="t min", default=0.0)
    t_max: bpy.props.FloatProperty(name="t max", default=2*np.pi)
    resolution: bpy.props.IntProperty(name="Résolution", default=200, min=10, max=2000)

    # === PRESETS (VERSION SÉCURISÉE) ===
    selected_preset: bpy.props.StringProperty(
        name="Preset sélectionné",
        default="NONE",
        description="Nom du preset sélectionné"
    )

    # Filtres simples
    preset_search: bpy.props.StringProperty(
        name="Rechercher",
        default="",
        description="Rechercher dans les presets"
    )

    show_preset_details: bpy.props.BoolProperty(
        name="Afficher détails",
        default=True,
        description="Afficher les détails du preset"
    )

    # === CRÉATION DE PRESETS ===
    new_preset_name: bpy.props.StringProperty(
        name="Nom du preset",
        default="",
        description="Nom pour le nouveau preset"
    )

    new_preset_description: bpy.props.StringProperty(
        name="Description",
        default="",
        description="Description du preset"
    )

    # === MESSAGES ===
    validation_message: bpy.props.StringProperty(
        name="Validation",
        default="",
        description="Message de validation"
    )

    preset_message: bpy.props.StringProperty(
        name="Message preset",
        default="",
        description="Message concernant les presets"
    )

# ============ FONCTIONS UTILITAIRES ============

def get_or_create_curve_tube_group():
    """Crée le node group pour les tubes"""
    group_name = "Curve Tube"
    gn = bpy.data.node_groups.get(group_name)
    if gn is not None:
        return gn

    curve_tube = bpy.data.node_groups.new(type='GeometryNodeTree', name=group_name)
    curve_tube.is_modifier = True

    # Interface
    out_socket = curve_tube.interface.new_socket(
        name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    in_socket_curve = curve_tube.interface.new_socket(
        name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    in_socket_radius = curve_tube.interface.new_socket(
        name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    in_socket_radius.default_value = 0.05

    # Nodes
    nodes = curve_tube.nodes
    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")
    curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")
    curve_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
    curve_circle.mode = 'RADIUS'
    curve_circle.inputs[0].default_value = 16

    # Links
    links = curve_tube.links
    links.new(curve_to_mesh.outputs[0], group_output.inputs[0])
    links.new(group_input.outputs[0], curve_to_mesh.inputs[0])
    links.new(curve_circle.outputs[0], curve_to_mesh.inputs[1])
    links.new(group_input.outputs[1], curve_circle.inputs[4])

    return curve_tube

# ============ OPÉRATEURS SIMPLIFIÉS ============

class PLAN_CURVES_OT_refresh_presets(bpy.types.Operator):
    """Rafraîchit la liste des presets"""
    bl_idname = "plan_curves.refresh_presets"
    bl_label = "Refresh Presets"
    bl_description = "Actualise la liste des presets"

    def execute(self, context):
        # Forcer le rafraîchissement en changeant une propriété
        props = context.scene.plan_curves_props
        current_type = props.curve_type
        props.curve_type = current_type  # Force update

        self.report({'INFO'}, "Liste des presets actualisée")
        return {'FINISHED'}

class PLAN_CURVES_OT_load_preset_simple(bpy.types.Operator):
    """Charge un preset par nom"""
    bl_idname = "plan_curves.load_preset_simple"
    bl_label = "Load Preset"
    bl_description = "Charge le preset sélectionné"

    preset_name: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.plan_curves_props

        if not self.preset_name or self.preset_name == 'NONE':
            self.report({'WARNING'}, get_text('no_preset_selected'))
            return {'CANCELLED'}

        manager = SimplePresetManager()
        preset_data = manager.get_preset_by_name(props.curve_type, self.preset_name)

        if not preset_data:
            self.report({'ERROR'}, get_text('preset_not_found'))
            return {'CANCELLED'}

        try:
            # Charger les données
            props.equation1 = preset_data.get('equation1', '')
            if 'equation2' in preset_data:
                props.equation2 = preset_data.get('equation2', 't')

            props.x_min = preset_data.get('x_min', -5.0)
            props.x_max = preset_data.get('x_max', 5.0)
            props.y_min = preset_data.get('y_min', -5.0)
            props.y_max = preset_data.get('y_max', 5.0)
            props.t_min = preset_data.get('t_min', 0.0)
            props.t_max = preset_data.get('t_max', 2*np.pi)
            props.resolution = preset_data.get('resolution', 200)

            props.selected_preset = self.preset_name
            props.preset_message = f"✓ {get_text('preset_loaded')}: '{self.preset_name}'"

            self.report({'INFO'}, f"{get_text('preset_loaded')}: '{self.preset_name}'")

        except Exception as e:
            self.report({'ERROR'}, f"Erreur: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class PLAN_CURVES_OT_create_preset_simple(bpy.types.Operator):
    """Crée un nouveau preset"""
    bl_idname = "plan_curves.create_preset_simple"
    bl_label = "Create Preset"
    bl_description = "Crée un nouveau preset avec les paramètres actuels"

    def execute(self, context):
        props = context.scene.plan_curves_props

        if not props.new_preset_name.strip():
            self.report({'ERROR'}, get_text('name_required'))
            return {'CANCELLED'}

        # Préparer les données
        preset_data = {
            'equation1': props.equation1,
            'equation2': props.equation2,
            'x_min': props.x_min,
            'x_max': props.x_max,
            'y_min': props.y_min,
            'y_max': props.y_max,
            't_min': props.t_min,
            't_max': props.t_max,
            'resolution': props.resolution,
            'description': props.new_preset_description or f"Preset utilisateur {props.curve_type}"
        }

        manager = SimplePresetManager()
        success, message = manager.create_preset(props.curve_type, props.new_preset_name, preset_data)

        if success:
            self.report({'INFO'}, message)
            props.preset_message = f"✓ {message}"
            # Réinitialiser
            props.new_preset_name = ""
            props.new_preset_description = ""
        else:
            self.report({'ERROR'}, message)
            props.preset_message = f"✗ {message}"
            return {'CANCELLED'}

        return {'FINISHED'}

class PLAN_CURVES_OT_delete_preset_simple(bpy.types.Operator):
    """Supprime un preset"""
    bl_idname = "plan_curves.delete_preset_simple"
    bl_label = "Delete Preset"
    bl_description = "Supprime le preset sélectionné"

    preset_name: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.plan_curves_props

        if not self.preset_name or self.preset_name == 'NONE':
            self.report({'WARNING'}, get_text('no_preset_selected'))
            return {'CANCELLED'}

        manager = SimplePresetManager()
        preset_data = manager.get_preset_by_name(props.curve_type, self.preset_name)

        if not preset_data or not preset_data.get('editable', False):
            self.report({'ERROR'}, get_text('cannot_delete'))
            return {'CANCELLED'}

        success, message = manager.delete_preset(props.curve_type, self.preset_name)

        if success:
            self.report({'INFO'}, message)
            props.preset_message = f"✓ {message}"
            props.selected_preset = "NONE"
        else:
            self.report({'ERROR'}, message)
            props.preset_message = f"✗ {message}"
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class PLAN_CURVES_OT_validate_params(bpy.types.Operator):
    """Valide les paramètres actuels"""
    bl_idname = "plan_curves.validate_params"
    bl_label = "Validate Parameters"
    bl_description = "Valide les paramètres actuels"

    def execute(self, context):
        props = context.scene.plan_curves_props

        # Préparer les données
        data = {
            'equation1': props.equation1,
            'equation2': props.equation2,
            'x_min': props.x_min,
            'x_max': props.x_max,
            'y_min': props.y_min,
            'y_max': props.y_max,
            't_min': props.t_min,
            't_max': props.t_max,
            'resolution': props.resolution
        }

        manager = SimplePresetManager()
        valid, message = manager.validate_preset_data(props.curve_type, data)

        props.validation_message = message

        if valid:
            self.report({'INFO'}, get_text('valid_params'))
        else:
            self.report({'ERROR'}, f"{get_text('validation_failed')}: {message}")

        return {'FINISHED'}

class PLAN_CURVES_OT_generate_curve(bpy.types.Operator):
    """Génère la courbe"""
    bl_idname = "plan_curves.generate_curve"
    bl_label = "Generate Curve"
    bl_description = "Génère la courbe selon les paramètres"

    def execute(self, context):
        props = context.scene.plan_curves_props

        if not SYMPY_AVAILABLE:
            self.report({'ERROR'}, get_text('sympy_not_installed'))
            # Afficher un message pour rediriger vers les préférences
            self.report({'INFO'}, get_text('sympy_required'))
            return {'CANCELLED'}

        # Valider d'abord
        bpy.ops.plan_curves.validate_params()
        if get_text('validation_failed').lower() in props.validation_message.lower():
            return {'CANCELLED'}

        try:
            if props.curve_type == 'EXPLICIT':
                return self.generate_explicit(context, props)
            elif props.curve_type == 'PARAMETRIC':
                return self.generate_parametric(context, props)
            elif props.curve_type == 'POLAR':
                return self.generate_polar(context, props)
            elif props.curve_type == 'IMPLICIT':
                return self.generate_implicit(context, props)
        except Exception as e:
            self.report({'ERROR'}, f"Erreur: {e}")
            return {'CANCELLED'}

    def add_geometry_nodes(self, obj):
        try:
            group = get_or_create_curve_tube_group()
            geo_mod = obj.modifiers.new(name="Tube", type='NODES')
            geo_mod.node_group = group
            geo_mod["Input_2"] = 0.05
        except Exception as e:
            print(f"Erreur Geometry Nodes: {e}")

    def generate_explicit(self, context, props):
        x = sp.symbols('x')
        f = sp.sympify(props.equation1)
        f_lambd = sp.lambdify(x, f, modules=['numpy'])

        x_vals = np.linspace(props.x_min, props.x_max, props.resolution)
        y_vals = f_lambd(x_vals)

        verts = [(float(xv), float(yv), 0.0) for xv, yv in zip(x_vals, y_vals) if np.isfinite(yv)]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        curve_data = bpy.data.curves.new("Courbe_Explicite", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(verts) - 1)

        for i, coord in enumerate(verts):
            spline.points[i].co = (*coord, 1.0)

        obj = bpy.data.objects.new("Courbe_Explicite", curve_data)
        context.collection.objects.link(obj)
        self.add_geometry_nodes(obj)

        self.report({'INFO'}, f"Courbe explicite créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_parametric(self, context, props):
        t = sp.symbols('t')
        fx = sp.sympify(props.equation1)
        fy = sp.sympify(props.equation2)

        fx_lambd = sp.lambdify(t, fx, modules=['numpy'])
        fy_lambd = sp.lambdify(t, fy, modules=['numpy'])

        t_vals = np.linspace(props.t_min, props.t_max, props.resolution)
        x_vals = fx_lambd(t_vals)
        y_vals = fy_lambd(t_vals)

        verts = [(float(xv), float(yv), 0.0) for xv, yv in zip(x_vals, y_vals)
                if np.isfinite(xv) and np.isfinite(yv)]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        curve_data = bpy.data.curves.new("Courbe_Parametrique", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(verts) - 1)

        for i, coord in enumerate(verts):
            spline.points[i].co = (*coord, 1.0)

        obj = bpy.data.objects.new("Courbe_Parametrique", curve_data)
        context.collection.objects.link(obj)
        self.add_geometry_nodes(obj)

        self.report({'INFO'}, f"Courbe paramétrique créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_polar(self, context, props):
        theta = sp.symbols('theta')
        fr = sp.sympify(props.equation1)
        fr_lambd = sp.lambdify(theta, fr, modules=['numpy'])

        theta_vals = np.linspace(props.t_min, props.t_max, props.resolution)
        r_vals = fr_lambd(theta_vals)

        x_vals = r_vals * np.cos(theta_vals)
        y_vals = r_vals * np.sin(theta_vals)

        verts = [(float(xv), float(yv), 0.0) for xv, yv in zip(x_vals, y_vals)
                if np.isfinite(xv) and np.isfinite(yv)]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        curve_data = bpy.data.curves.new("Courbe_Polaire", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(verts) - 1)

        for i, coord in enumerate(verts):
            spline.points[i].co = (*coord, 1.0)

        obj = bpy.data.objects.new("Courbe_Polaire", curve_data)
        context.collection.objects.link(obj)
        self.add_geometry_nodes(obj)

        self.report({'INFO'}, f"Courbe polaire créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_implicit(self, context, props):
        x, y = sp.symbols('x y')
        F = sp.sympify(props.equation1)
        f_lambd = sp.lambdify((x, y), F, modules=['numpy'])

        x_vals = np.linspace(props.x_min, props.x_max, 100)
        y_vals = np.linspace(props.y_min, props.y_max, 100)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = f_lambd(X, Y)

        verts = []
        for i in range(X.shape[0]):
            for j in range(X.shape[1]-1):
                if np.sign(Z[i,j]) != np.sign(Z[i,j+1]):
                    t = abs(Z[i,j]) / (abs(Z[i,j]) + abs(Z[i,j+1]))
                    x0 = X[i,j]*(1-t) + X[i,j+1]*t
                    y0 = Y[i,j]*(1-t) + Y[i,j+1]*t
                    verts.append((float(x0), float(y0), 0.0))

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('no_curve_detected'))
            return {'CANCELLED'}

        curve_data = bpy.data.curves.new("Courbe_Implicite", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(verts) - 1)

        for i, coord in enumerate(verts):
            spline.points[i].co = (*coord, 1.0)

        obj = bpy.data.objects.new("Courbe_Implicite", curve_data)
        context.collection.objects.link(obj)
        self.add_geometry_nodes(obj)

        self.report({'INFO'}, f"Courbe implicite créée ({len(verts)} segments)")
        return {'FINISHED'}

# ============ PANNEAUX UI SIMPLIFIÉS ============

class PLAN_CURVES_PT_main(bpy.types.Panel):
    """Panneau principal"""
    bl_label = "Courbes du Plan"
    bl_idname = "PLAN_CURVES_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Courbes"

    def draw(self, context):
        layout = self.layout
        props = context.scene.plan_curves_props

        # Vérification SymPy
        if not SYMPY_AVAILABLE:
            warning_box = layout.box()
            warning_box.alert = True
            warning_box.label(text=get_text('sympy_not_installed'), icon='ERROR')
            warning_box.label(text=get_text('sympy_required'))
            warning_box.operator("screen.userpref_show", text="Ouvrir les Préférences", icon='PREFERENCES')
            layout.separator()

        # Type de courbe
        layout.prop(props, "curve_type", text=get_text('curve_type'))

        # Équations
        eq_box = layout.box()
        eq_box.label(text=get_text('equations'), icon='SYNTAX_ON')

        if props.curve_type == 'EXPLICIT':
            eq_box.prop(props, "equation1", text="y =")
        elif props.curve_type == 'PARAMETRIC':
            eq_box.prop(props, "equation1", text="x(t) =")
            eq_box.prop(props, "equation2", text="y(t) =")
        elif props.curve_type == 'POLAR':
            eq_box.prop(props, "equation1", text="r(θ) =")
        elif props.curve_type == 'IMPLICIT':
            eq_box.prop(props, "equation1", text="F(x,y) = 0")

        # Paramètres
        param_box = layout.box()
        param_box.label(text=get_text('parameters'), icon='SETTINGS')

        if props.curve_type in ['EXPLICIT', 'IMPLICIT']:
            col = param_box.column(align=True)
            col.prop(props, "x_min")
            col.prop(props, "x_max")

        if props.curve_type == 'IMPLICIT':
            col = param_box.column(align=True)
            col.prop(props, "y_min")
            col.prop(props, "y_max")

        if props.curve_type in ['PARAMETRIC', 'POLAR']:
            col = param_box.column(align=True)
            if props.curve_type == 'POLAR':
                col.prop(props, "t_min", text="θ min")
                col.prop(props, "t_max", text="θ max")
            else:
                col.prop(props, "t_min")
                col.prop(props, "t_max")

        param_box.prop(props, "resolution", text=get_text('resolution'))

        # Validation
        val_box = layout.box()
        val_box.label(text=get_text('validation'), icon='CHECKMARK')
        val_box.operator("plan_curves.validate_params", text=get_text('validate'), icon='FILE_REFRESH')

        if props.validation_message:
            msg_box = val_box.box()
            if "valide" in props.validation_message.lower() or "valid" in props.validation_message.lower():
                msg_box.label(text=props.validation_message, icon='CHECKMARK')
            else:
                msg_box.label(text=props.validation_message, icon='ERROR')

        # Génération
        layout.separator()
        row = layout.row()
        row.scale_y = 1.5
        row.enabled = SYMPY_AVAILABLE  # Désactiver si SymPy n'est pas disponible
        row.operator("plan_curves.generate_curve", text=get_text('generate_curve'), icon='CURVE_DATA')

class PLAN_CURVES_PT_presets(bpy.types.Panel):
    """Panneau des presets"""
    bl_label = get_text('presets')
    bl_idname = "PLAN_CURVES_PT_presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Courbes"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.plan_curves_props

        # Navigation
        nav_box = layout.box()
        nav_box.label(text=get_text('navigation'), icon='FILEBROWSER')

        # Liste des presets
        manager = SimplePresetManager()
        preset_names = manager.get_preset_names(props.curve_type)

        if preset_names:
            col = nav_box.column(align=True)
            for name in preset_names:
                row = col.row(align=True)

                # Bouton de chargement
                op = row.operator("plan_curves.load_preset_simple", text=name, icon='IMPORT')
                op.preset_name = name

                # Bouton de suppression pour presets utilisateur
                preset_data = manager.get_preset_by_name(props.curve_type, name)
                if preset_data and preset_data.get('editable', False):
                    op_del = row.operator("plan_curves.delete_preset_simple", text="", icon='TRASH')
                    op_del.preset_name = name
        else:
            nav_box.label(text=get_text('no_presets'))

        # Rafraîchir
        nav_box.operator("plan_curves.refresh_presets", text=get_text('refresh'), icon='FILE_REFRESH')

        # Détails du preset sélectionné
        if props.selected_preset != "NONE" and props.show_preset_details:
            self.draw_preset_details(nav_box, props, manager)

        # Création de preset
        layout.separator()
        create_box = layout.box()
        create_box.label(text=get_text('create_preset'), icon='PLUS')
        create_box.prop(props, "new_preset_name", text=get_text('preset_name'))
        create_box.prop(props, "new_preset_description", text=get_text('description'))
        create_box.operator("plan_curves.create_preset_simple", icon='FILE_NEW')

        # Messages
        if props.preset_message:
            msg_box = layout.box()
            if "✓" in props.preset_message:
                msg_box.label(text=props.preset_message, icon='CHECKMARK')
            else:
                msg_box.label(text=props.preset_message, icon='ERROR')

    def draw_preset_details(self, parent_layout, props, manager):
        """Affiche les détails du preset sélectionné"""
        try:
            preset_data = manager.get_preset_by_name(props.curve_type, props.selected_preset)

            if preset_data:
                details_box = parent_layout.box()
                details_box.label(text=get_text('details'), icon='INFO')
                details_box.label(text=f"Nom: {props.selected_preset}")

                if 'description' in preset_data:
                    desc = preset_data['description']
                    details_box.label(text=f"{get_text('description')}: {desc}")

                if 'equation1' in preset_data:
                    eq = preset_data['equation1'][:30] + "..." if len(preset_data['equation1']) > 30 else preset_data['equation1']
                    details_box.label(text=f"{get_text('equation')} {eq}")

                source = get_text('default_source') if preset_data.get('source') == 'default' else get_text('user_source')
                details_box.label(text=f"{get_text('source')} {source}")

        except Exception as e:
            print(f"Erreur détails preset: {e}")

# ============ ENREGISTREMENT ============

classes = (
    PLAN_CURVES_AddonPreferences,
    PLAN_CURVES_OT_check_sympy,
    PLAN_CURVES_OT_install_sympy,
    PlanCurvesProperties,
    PLAN_CURVES_OT_refresh_presets,
    PLAN_CURVES_OT_load_preset_simple,
    PLAN_CURVES_OT_create_preset_simple,
    PLAN_CURVES_OT_delete_preset_simple,
    PLAN_CURVES_OT_validate_params,
    PLAN_CURVES_OT_generate_curve,
    PLAN_CURVES_PT_main,
    PLAN_CURVES_PT_presets,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.plan_curves_props = bpy.props.PointerProperty(type=PlanCurvesProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if hasattr(bpy.types.Scene, 'plan_curves_props'):
        del bpy.types.Scene.plan_curves_props

if __name__ == "__main__":
    register()
