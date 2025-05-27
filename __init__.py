from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Any

bl_info = {
    "name": "Courbes du Plan - Presets Fixes",
    "description": "Système stable de gestion de presets pour courbes mathématiques",
    "author": "TonNom + Assistant",
    "version": (4, 2, 1),  # ✅ Version incrémentée pour compatibilité 4.4.3
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > Courbes du Plan",
    "category": "Add Curve"
}

import bpy
from bpy.types import PropertyGroup

# ✅ AJOUT: Vérifications de compatibilité
def check_blender_version() -> bool:
    """
    Vérifie la compatibilité avec la version de Blender.
    
    Returns:
        True si compatible (>= 4.4.0), False sinon
    """
    required = (4, 4, 0)
    current = bpy.app.version
    return current >= required

def get_version_info() -> tuple[str, str]:
    """
    Retourne les informations de version.
    
    Returns:
        Tuple (version_actuelle, version_requise)
    """
    current = ".".join(map(str, bpy.app.version))
    required = ".".join(map(str, (4, 4, 0)))
    return current, required

# ✅ Importation sécurisée des modules
try:
    # Importation des modules
    from . import preferences
    from . import properties
    from . import operators
    from . import panels
    from . import utils

    # Liste des modules pour l'enregistrement
    modules: List[Any] = [
        preferences,
        properties,
        operators,
        panels,
        utils
    ]
    
    MODULES_LOADED = True
    print("✅ Tous les modules 'Courbes du Plan' chargés")
    
except ImportError as e:
    print(f"❌ Erreur importation modules 'Courbes du Plan': {e}")
    modules = []
    MODULES_LOADED = False

def register() -> None:
    """Enregistre tous les modules de l'addon avec vérifications complètes."""
    
    # ✅ VÉRIFICATION 1: Version Blender
    if not check_blender_version():
        current, required = get_version_info()
        error_msg = (
            f"❌ L'addon 'Courbes du Plan' nécessite Blender {required}+ "
            f"(version actuelle: {current})"
        )
        print(error_msg)
        raise RuntimeError(error_msg)
    
    # ✅ VÉRIFICATION 2: Modules chargés
    if not MODULES_LOADED:
        error_msg = (
            "❌ Impossible de charger les modules de l'addon. "
            "Vérifiez l'installation et les dépendances."
        )
        print(error_msg)
        raise RuntimeError(error_msg)
    
    current_version, _ = get_version_info()
    print(f"🚀 Démarrage addon 'Courbes du Plan' v{bl_info['version']} - Blender {current_version}")
    
    # ✅ ENREGISTREMENT SÉCURISÉ
    registered_modules = []
    
    try:
        # Enregistrer les modules un par un
        for module in modules:
            if hasattr(module, 'register'):
                module.register()
                registered_modules.append(module)
                print(f"  ✅ {module.__name__.split('.')[-1]}")
            else:
                print(f"  ⚠️ Module {module.__name__} sans fonction register()")

        # Enregistrer les propriétés de scène
        bpy.types.Scene.plan_curves_props = bpy.props.PointerProperty(
            type=properties.PlanCurvesProperties
        )
        print("  ✅ Propriétés de scène")
        
        print("✅ Addon 'Courbes du Plan' activé avec succès!")
        
    except Exception as e:
        # ✅ NETTOYAGE automatique en cas d'erreur
        print(f"❌ Erreur lors de l'enregistrement: {e}")
        
        # Désenregistrer les modules déjà enregistrés
        for module in reversed(registered_modules):
            try:
                if hasattr(module, 'unregister'):
                    module.unregister()
                    print(f"  🔄 Nettoyage {module.__name__.split('.')[-1]}")
            except Exception as cleanup_error:
                print(f"  ⚠️ Erreur nettoyage: {cleanup_error}")
        
        # Supprimer les propriétés si elles ont été créées
        try:
            if hasattr(bpy.types.Scene, 'plan_curves_props'):
                del bpy.types.Scene.plan_curves_props
        except:
            pass
        
        raise RuntimeError(f"Impossible d'enregistrer l'addon: {e}")

def unregister() -> None:
    """Désenregistre tous les modules de l'addon de manière sécurisée."""
    
    print("🔄 Désactivation addon 'Courbes du Plan'...")
    
    # ✅ Supprimer les propriétés de scène en premier
    try:
        if hasattr(bpy.types.Scene, 'plan_curves_props'):
            del bpy.types.Scene.plan_curves_props
            print("  ✅ Propriétés de scène supprimées")
    except Exception as e:
        print(f"  ⚠️ Erreur suppression propriétés: {e}")

    # ✅ Désenregistrer les modules dans l'ordre inverse
    for module in reversed(modules):
        try:
            if hasattr(module, 'unregister'):
                module.unregister()
                print(f"  ✅ {module.__name__.split('.')[-1]}")
        except Exception as e:
            print(f"  ⚠️ Erreur {module.__name__.split('.')[-1]}: {e}")
    
    print("✅ Addon 'Courbes du Plan' désactivé!")

# ✅ DIAGNOSTIC - Fonction utilitaire
def get_addon_diagnostic() -> dict:
    """
    Retourne les informations de diagnostic de l'addon.
    
    Returns:
        Dictionnaire avec les informations système
    """
    current, required = get_version_info()
    return {
        'addon_name': bl_info['name'],
        'addon_version': bl_info['version'],
        'blender_current': current,
        'blender_required': required,
        'compatible': check_blender_version(),
        'modules_loaded': MODULES_LOADED,
        'modules_count': len(modules) if MODULES_LOADED else 0,
        'status': 'OK' if (check_blender_version() and MODULES_LOADED) else 'ERROR'
    }

# ✅ Auto-test pour développement
if __name__ == "__main__":
    try:
        print("🧪 Mode test direct...")
        print(f"📊 Diagnostic: {get_addon_diagnostic()}")
        register()
        print("✅ Test réussi - Addon enregistré")
    except Exception as e:
        print(f"❌ Échec du test: {e}")

# ✅ Affichage diagnostic au chargement (mode normal)
else:
    diagnostic = get_addon_diagnostic()
    if diagnostic['status'] == 'OK':
        print(f"📋 Addon prêt: {diagnostic['addon_name']} v{diagnostic['addon_version']}")
    else:
        print(f"⚠️ Problème potentiel: {diagnostic}")