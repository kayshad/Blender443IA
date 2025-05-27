# ===============================================
# FICHIER: utils.py (Fonctions utilitaires avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from bpy.types import GeometryNodeTree

import bpy

def get_or_create_curve_tube_group() -> GeometryNodeTree:
    """
    Crée ou récupère le node group pour les tubes de courbes.

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

    except Exception as e:
        raise RuntimeError(f"Impossible de créer le node group: {e}")

def register() -> None:
    """Enregistre les fonctions du module utils."""
    pass

def unregister() -> None:
    """Désenregistre les fonctions du module utils."""
    pass

