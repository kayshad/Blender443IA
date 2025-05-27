# ===============================================
# FICHIER: utils.py (Fonctions utilitaires avec annotations - CORRIGÉ 4.4.3)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from bpy.types import GeometryNodeTree, NodeSocket

import bpy

def get_or_create_curve_tube_group() -> GeometryNodeTree:
    """
    Crée ou récupère le node group pour les tubes de courbes.
    ✅ VERSION CORRIGÉE POUR BLENDER 4.4.3

    Returns:
        Node group pour la conversion courbe vers tube

    Raises:
        RuntimeError: Si impossible de créer le node group
    """
    group_name: str = "Curve Tube"
    gn: Optional[GeometryNodeTree] = bpy.data.node_groups.get(group_name)

    if gn is not None:
        return gn

    try:
        curve_tube: GeometryNodeTree = bpy.data.node_groups.new(
            type='GeometryNodeTree',
            name=group_name
        )
        curve_tube.is_modifier = True

        # ✅ CORRECTION CRITIQUE: Interface corrigée pour Blender 4.4.3
        # Ancien: new_socket(name, in_out, socket_type)
        # Nouveau: new_socket(name, socket_type, in_out)
        
        out_socket: NodeSocket = curve_tube.interface.new_socket(
            name="Geometry",
            socket_type='NodeSocketGeometry',
            in_out='OUTPUT'
        )
        
        in_socket_curve: NodeSocket = curve_tube.interface.new_socket(
            name="Curve",
            socket_type='NodeSocketGeometry',
            in_out='INPUT'
        )
        
        in_socket_radius: NodeSocket = curve_tube.interface.new_socket(
            name="Radius",
            socket_type='NodeSocketFloat',
            in_out='INPUT'
        )
        
        # ✅ Configuration valeur par défaut sécurisée
        if hasattr(in_socket_radius, 'default_value'):
            in_socket_radius.default_value = 0.05

        # Nodes
        nodes = curve_tube.nodes
        group_input = nodes.new("NodeGroupInput")
        group_output = nodes.new("NodeGroupOutput")
        curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")
        curve_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
        
        # ✅ Configuration du cercle avec vérifications
        curve_circle.mode = 'RADIUS'
        if len(curve_circle.inputs) > 0 and hasattr(curve_circle.inputs[0], 'default_value'):
            curve_circle.inputs[0].default_value = 16

        # ✅ Positionnement pour une meilleure lisibilité
        group_input.location = (-200, 0)
        curve_to_mesh.location = (0, 0)
        curve_circle.location = (-200, -150)
        group_output.location = (200, 0)

        # ✅ Links avec vérifications sécurisées
        links = curve_tube.links
        
        try:
            links.new(curve_to_mesh.outputs[0], group_output.inputs[0])
            links.new(group_input.outputs[0], curve_to_mesh.inputs[0])
            links.new(curve_circle.outputs[0], curve_to_mesh.inputs[1])
            
            # Connexion radius si disponible
            if len(group_input.outputs) > 1 and len(curve_circle.inputs) > 4:
                links.new(group_input.outputs[1], curve_circle.inputs[4])
                
        except IndexError as e:
            print(f"Avertissement connexions geometry nodes: {e}")

        return curve_tube

    except Exception as e:
        raise RuntimeError(f"Impossible de créer le node group: {e}")

def check_blender_version_compatibility() -> bool:
    """
    Vérifie la compatibilité avec Blender 4.4.3+
    
    Returns:
        True si compatible
    """
    required = (4, 4, 0)
    current = bpy.app.version
    return current >= required

def get_blender_version_string() -> str:
    """
    Retourne la version Blender formatée
    
    Returns:
        Version sous forme "X.Y.Z"
    """
    return ".".join(map(str, bpy.app.version))

def register() -> None:
    """Enregistre les fonctions du module utils avec vérifications."""
    if not check_blender_version_compatibility():
        print(f"⚠️ Blender {get_blender_version_string()} - Addon optimisé pour 4.4.3+")

def unregister() -> None:
    """Désenregistre les fonctions du module utils."""
    pass