from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Any

bl_info = {
    "name": "Courbes du Plan - Presets Fixes",
    "description": "Système stable de gestion de presets pour courbes mathématiques",
    "author": "TonNom + Assistant",
    "version": (4, 2),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > Courbes du Plan",
    "category": "Add Curve"
}

import bpy
from bpy.types import PropertyGroup

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

def register() -> None:
    """Enregistre tous les modules de l'addon."""
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

    # Enregistrer les propriétés de scène
    bpy.types.Scene.plan_curves_props = bpy.props.PointerProperty(
        type=properties.PlanCurvesProperties
    )

def unregister() -> None:
    """Désenregistre tous les modules de l'addon."""
    # Supprimer les propriétés de scène
    if hasattr(bpy.types.Scene, 'plan_curves_props'):
        del bpy.types.Scene.plan_curves_props

    # Désenregistrer les modules dans l'ordre inverse
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()

if __name__ == "__main__":
    register()
