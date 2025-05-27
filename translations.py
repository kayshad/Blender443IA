# ===============================================
# FICHIER: translations.py (Dictionnaires de traduction avec annotations)
# ===============================================

from __future__ import annotations
from typing import Dict, Any

# Type alias pour améliorer la lisibilité
TranslationDict = Dict[str, str]
LanguageDict = Dict[str, TranslationDict]

TRANSLATIONS: LanguageDict = {
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

