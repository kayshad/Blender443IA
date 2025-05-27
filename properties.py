# ===============================================
# FICHIER: properties.py (Propriétés du groupe avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple, Any

if TYPE_CHECKING:
    from bpy.types import Context

import bpy
import numpy as np
from bpy.types import PropertyGroup

from .preset_manager import SimplePresetManager
from .preferences import get_text

# Type alias pour les items d'enum
EnumItem = Tuple[str, str, str]
EnumItems = List[EnumItem]

def get_preset_enum_items(self: PlanCurvesProperties, context: Context) -> EnumItems:
    """
    Items pour le menu des presets - Version sécurisée avec annotations.

    Args:
        self: Instance des propriétés
        context: Contexte Blender

    Returns:
        Liste des items d'enum pour les presets
    """
    try:
        curve_type: str = getattr(self, 'curve_type', 'EXPLICIT')
        manager: SimplePresetManager = SimplePresetManager()
        preset_names: List[str] = manager.get_preset_names(curve_type)

        items: EnumItems = [('NONE', get_text('select_preset'), get_text('no_preset'))]

        for name in preset_names:
            preset_data = manager.get_preset_by_name(curve_type, name)
            if preset_data:
                desc: str = preset_data.get('description', 'Pas de description')
                items.append((name, name, desc))

        return items

    except Exception as e:
        print(f"Erreur get_preset_enum_items: {e}")
        return [('NONE', 'Erreur', 'Erreur de chargement')]

class PlanCurvesProperties(PropertyGroup):
    """Propriétés principales simplifiées avec annotations complètes."""

    # === PROPRIÉTÉS DE BASE ===
    curve_type: bpy.props.EnumProperty(  # type: ignore
        name="Type de courbe",
        items=[
            ('EXPLICIT', "Explicite (y=f(x))", "Fonction explicite"),
            ('PARAMETRIC', "Paramétrique (x(t),y(t))", "Courbe paramétrique"),
            ('POLAR', "Polaire (r=f(θ))", "Coordonnées polaires"),
            ('IMPLICIT', "Implicite (F(x,y)=0)", "Équation implicite"),
        ],
        default='EXPLICIT'
    )

    equation1: bpy.props.StringProperty(  # type: ignore
        name="Équation 1",
        default="x**2",
        description="Première équation ou équation principale"
    )

    equation2: bpy.props.StringProperty(  # type: ignore
        name="Équation 2",
        default="t",
        description="Deuxième équation pour les courbes paramétriques"
    )

    x_min: bpy.props.FloatProperty(  # type: ignore
        name="x min",
        default=-5.0,
        description="Valeur minimale de x"
    )

    x_max: bpy.props.FloatProperty(  # type: ignore
        name="x max",
        default=5.0,
        description="Valeur maximale de x"
    )

    y_min: bpy.props.FloatProperty(  # type: ignore
        name="y min",
        default=-5.0,
        description="Valeur minimale de y"
    )

    y_max: bpy.props.FloatProperty(  # type: ignore
        name="y max",
        default=5.0,
        description="Valeur maximale de y"
    )

    t_min: bpy.props.FloatProperty(  # type: ignore
        name="t min",
        default=0.0,
        description="Valeur minimale du paramètre t"
    )

    t_max: bpy.props.FloatProperty(  # type: ignore
        name="t max",
        default=2*np.pi,
        description="Valeur maximale du paramètre t"
    )

    resolution: bpy.props.IntProperty(  # type: ignore
        name="Résolution",
        default=200,
        min=10,
        max=2000,
        description="Nombre de points pour la courbe"
    )

    # === PRESETS (VERSION SÉCURISÉE) ===
    selected_preset: bpy.props.StringProperty(  # type: ignore
        name="Preset sélectionné",
        default="NONE",
        description="Nom du preset sélectionné"
    )

    preset_search: bpy.props.StringProperty(  # type: ignore
        name="Rechercher",
        default="",
        description="Rechercher dans les presets"
    )

    show_preset_details: bpy.props.BoolProperty(  # type: ignore
        name="Afficher détails",
        default=True,
        description="Afficher les détails du preset"
    )

    # === CRÉATION DE PRESETS ===
    new_preset_name: bpy.props.StringProperty(  # type: ignore
        name="Nom du preset",
        default="",
        description="Nom pour le nouveau preset"
    )

    new_preset_description: bpy.props.StringProperty(  # type: ignore
        name="Description",
        default="",
        description="Description du preset"
    )

    # === MESSAGES ===
    validation_message: bpy.props.StringProperty(  # type: ignore
        name="Validation",
        default="",
        description="Message de validation"
    )

    preset_message: bpy.props.StringProperty(  # type: ignore
        name="Message preset",
        default="",
        description="Message concernant les presets"
    )

# Classes à enregistrer
classes: Tuple[type, ...] = (
    PlanCurvesProperties,
)

def register() -> None:
    """Enregistre les classes du module properties."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister() -> None:
    """Désenregistre les classes du module properties."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

