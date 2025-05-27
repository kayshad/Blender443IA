# ===============================================
# FICHIER: operators.py (Tous les opérateurs avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Set, List, Tuple, Optional, Union, Callable

if TYPE_CHECKING:
    from bpy.types import Context, Object, Curve, Spline
    import numpy.typing as npt

import bpy
import numpy as np
import numpy.typing as npt
from bpy.types import Operator

from .preset_manager import SimplePresetManager, PresetData
from .preferences import get_text, SYMPY_AVAILABLE
from .utils import get_or_create_curve_tube_group

try:
    import sympy as sp
    from sympy import symbols, sympify, lambdify
    from sympy.core.expr import Expr
    from sympy.core.symbol import Symbol
    NDArrayFloat = npt.NDArray[np.floating]
except ImportError:
    sp = None
    NDArrayFloat = None

# Type aliases
OperatorReturn = Set[str]
Vertex3D = Tuple[float, float, float]
VertexList = List[Vertex3D]

class PLAN_CURVES_OT_refresh_presets(Operator):
    """Rafraîchit la liste des presets."""

    bl_idname: str = "plan_curves.refresh_presets"
    bl_label: str = "Refresh Presets"
    bl_description: str = "Actualise la liste des presets"

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute le rafraîchissement des presets.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        # Forcer le rafraîchissement en changeant une propriété
        props = context.scene.plan_curves_props
        current_type: str = props.curve_type
        props.curve_type = current_type  # Force update

        self.report({'INFO'}, "Liste des presets actualisée")
        return {'FINISHED'}

class PLAN_CURVES_OT_load_preset_simple(Operator):
    """Charge un preset par nom."""

    bl_idname: str = "plan_curves.load_preset_simple"
    bl_label: str = "Load Preset"
    bl_description: str = "Charge le preset sélectionné"

    preset_name: bpy.props.StringProperty()  # type: ignore

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute le chargement d'un preset.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        props = context.scene.plan_curves_props

        if not self.preset_name or self.preset_name == 'NONE':
            self.report({'WARNING'}, get_text('no_preset_selected'))
            return {'CANCELLED'}

        manager: SimplePresetManager = SimplePresetManager()
        preset_data: Optional[PresetData] = manager.get_preset_by_name(
            props.curve_type, self.preset_name
        )

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

class PLAN_CURVES_OT_create_preset_simple(Operator):
    """Crée un nouveau preset."""

    bl_idname: str = "plan_curves.create_preset_simple"
    bl_label: str = "Create Preset"
    bl_description: str = "Crée un nouveau preset avec les paramètres actuels"

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute la création d'un nouveau preset.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        props = context.scene.plan_curves_props

        if not props.new_preset_name.strip():
            self.report({'ERROR'}, get_text('name_required'))
            return {'CANCELLED'}

        # Préparer les données
        preset_data: PresetData = {
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

        manager: SimplePresetManager = SimplePresetManager()
        success, message = manager.create_preset(
            props.curve_type, props.new_preset_name, preset_data
        )

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

class PLAN_CURVES_OT_delete_preset_simple(Operator):
    """Supprime un preset."""

    bl_idname: str = "plan_curves.delete_preset_simple"
    bl_label: str = "Delete Preset"
    bl_description: str = "Supprime le preset sélectionné"

    preset_name: bpy.props.StringProperty()  # type: ignore

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute la suppression d'un preset.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        props = context.scene.plan_curves_props

        if not self.preset_name or self.preset_name == 'NONE':
            self.report({'WARNING'}, get_text('no_preset_selected'))
            return {'CANCELLED'}

        manager: SimplePresetManager = SimplePresetManager()
        preset_data: Optional[PresetData] = manager.get_preset_by_name(
            props.curve_type, self.preset_name
        )

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

    def invoke(self, context: Context, event) -> OperatorReturn:
        """
        Invoque la confirmation de suppression.

        Args:
            context: Contexte Blender
            event: Événement déclencheur

        Returns:
            Statut d'invocation
        """
        return context.window_manager.invoke_confirm(self, event)

class PLAN_CURVES_OT_validate_params(Operator):
    """Valide les paramètres actuels."""

    bl_idname: str = "plan_curves.validate_params"
    bl_label: str = "Validate Parameters"
    bl_description: str = "Valide les paramètres actuels"

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute la validation des paramètres.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        props = context.scene.plan_curves_props

        # Préparer les données
        data: PresetData = {
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

        manager: SimplePresetManager = SimplePresetManager()
        valid, message = manager.validate_preset_data(props.curve_type, data)

        props.validation_message = message

        if valid:
            self.report({'INFO'}, get_text('valid_params'))
        else:
            self.report({'ERROR'}, f"{get_text('validation_failed')}: {message}")

        return {'FINISHED'}

class PLAN_CURVES_OT_generate_curve(Operator):
    """Génère la courbe."""

    bl_idname: str = "plan_curves.generate_curve"
    bl_label: str = "Generate Curve"
    bl_description: str = "Génère la courbe selon les paramètres"

    def execute(self, context: Context) -> OperatorReturn:
        """
        Exécute la génération de courbe.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        props = context.scene.plan_curves_props

        if not SYMPY_AVAILABLE:
            self.report({'ERROR'}, get_text('sympy_not_installed'))
            self.report({'INFO'}, get_text('sympy_required'))
            return {'CANCELLED'}

        # Valider d'abord
        bpy.ops.plan_curves.validate_params()
        if get_text('validation_failed').lower() in props.validation_message.lower():
            return {'CANCELLED'}

        try:
            curve_generators = {
                'EXPLICIT': self.generate_explicit,
                'PARAMETRIC': self.generate_parametric,
                'POLAR': self.generate_polar,
                'IMPLICIT': self.generate_implicit
            }

            generator = curve_generators.get(props.curve_type)
            if generator:
                return generator(context, props)
            else:
                self.report({'ERROR'}, f"Type de courbe non supporté: {props.curve_type}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Erreur: {e}")
            return {'CANCELLED'}

    def add_geometry_nodes(self, obj: Object) -> None:
        """
        Ajoute les geometry nodes pour le tube.

        Args:
            obj: Objet courbe à modifier
        """
        try:
            group = get_or_create_curve_tube_group()
            geo_mod = obj.modifiers.new(name="Tube", type='NODES')
            geo_mod.node_group = group
            geo_mod["Input_2"] = 0.05
        except Exception as e:
            print(f"Erreur Geometry Nodes: {e}")

    def create_curve_object(self, name: str, vertices: VertexList, context: Context) -> Object:
        """
        Crée un objet courbe à partir d'une liste de vertices.

        Args:
            name: Nom de l'objet courbe
            vertices: Liste des points de la courbe
            context: Contexte Blender

        Returns:
            Objet courbe créé
        """
        curve_data: Curve = bpy.data.curves.new(name, type='CURVE')
        curve_data.dimensions = '3D'
        spline: Spline = curve_data.splines.new('POLY')
        spline.points.add(len(vertices) - 1)

        for i, coord in enumerate(vertices):
            spline.points[i].co = (*coord, 1.0)

        obj: Object = bpy.data.objects.new(name, curve_data)
        context.collection.objects.link(obj)
        self.add_geometry_nodes(obj)

        return obj

    def generate_explicit(self, context: Context, props) -> OperatorReturn:
        """
        Génère une courbe explicite y = f(x).

        Args:
            context: Contexte Blender
            props: Propriétés de l'addon

        Returns:
            Statut d'exécution
        """
        if sp is None:
            return {'CANCELLED'}

        x: Symbol = sp.symbols('x')
        f: Expr = sp.sympify(props.equation1)
        f_lambd: Callable = sp.lambdify(x, f, modules=['numpy'])

        x_vals: NDArrayFloat = np.linspace(props.x_min, props.x_max, props.resolution)
        y_vals: NDArrayFloat = f_lambd(x_vals)

        verts: VertexList = [
            (float(xv), float(yv), 0.0)
            for xv, yv in zip(x_vals, y_vals)
            if np.isfinite(yv)
        ]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        self.create_curve_object("Courbe_Explicite", verts, context)
        self.report({'INFO'}, f"Courbe explicite créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_parametric(self, context: Context, props) -> OperatorReturn:
        """
        Génère une courbe paramétrique x(t), y(t).

        Args:
            context: Contexte Blender
            props: Propriétés de l'addon

        Returns:
            Statut d'exécution
        """
        if sp is None:
            return {'CANCELLED'}

        t: Symbol = sp.symbols('t')
        fx: Expr = sp.sympify(props.equation1)
        fy: Expr = sp.sympify(props.equation2)

        fx_lambd: Callable = sp.lambdify(t, fx, modules=['numpy'])
        fy_lambd: Callable = sp.lambdify(t, fy, modules=['numpy'])

        t_vals: NDArrayFloat = np.linspace(props.t_min, props.t_max, props.resolution)
        x_vals: NDArrayFloat = fx_lambd(t_vals)
        y_vals: NDArrayFloat = fy_lambd(t_vals)

        verts: VertexList = [
            (float(xv), float(yv), 0.0)
            for xv, yv in zip(x_vals, y_vals)
            if np.isfinite(xv) and np.isfinite(yv)
        ]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        self.create_curve_object("Courbe_Parametrique", verts, context)
        self.report({'INFO'}, f"Courbe paramétrique créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_polar(self, context: Context, props) -> OperatorReturn:
        """
        Génère une courbe polaire r = f(θ).

        Args:
            context: Contexte Blender
            props: Propriétés de l'addon

        Returns:
            Statut d'exécution
        """
        if sp is None:
            return {'CANCELLED'}

        theta: Symbol = sp.symbols('theta')
        fr: Expr = sp.sympify(props.equation1)
        fr_lambd: Callable = sp.lambdify(theta, fr, modules=['numpy'])

        theta_vals: NDArrayFloat = np.linspace(props.t_min, props.t_max, props.resolution)
        r_vals: NDArrayFloat = fr_lambd(theta_vals)

        x_vals: NDArrayFloat = r_vals * np.cos(theta_vals)
        y_vals: NDArrayFloat = r_vals * np.sin(theta_vals)

        verts: VertexList = [
            (float(xv), float(yv), 0.0)
            for xv, yv in zip(x_vals, y_vals)
            if np.isfinite(xv) and np.isfinite(yv)
        ]

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('not_enough_points'))
            return {'CANCELLED'}

        self.create_curve_object("Courbe_Polaire", verts, context)
        self.report({'INFO'}, f"Courbe polaire créée ({len(verts)} points)")
        return {'FINISHED'}

    def generate_implicit(self, context: Context, props) -> OperatorReturn:
        """
        Génère une courbe implicite F(x,y) = 0.

        Args:
            context: Contexte Blender
            props: Propriétés de l'addon

        Returns:
            Statut d'exécution
        """
        if sp is None:
            return {'CANCELLED'}

        x, y = sp.symbols('x y')
        F: Expr = sp.sympify(props.equation1)
        f_lambd: Callable = sp.lambdify((x, y), F, modules=['numpy'])

        x_vals: NDArrayFloat = np.linspace(props.x_min, props.x_max, 100)
        y_vals: NDArrayFloat = np.linspace(props.y_min, props.y_max, 100)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z: NDArrayFloat = f_lambd(X, Y)

        verts: VertexList = []
        for i in range(X.shape[0]):
            for j in range(X.shape[1]-1):
                if np.sign(Z[i,j]) != np.sign(Z[i,j+1]):
                    t: float = abs(Z[i,j]) / (abs(Z[i,j]) + abs(Z[i,j+1]))
                    x0: float = X[i,j]*(1-t) + X[i,j+1]*t
                    y0: float = Y[i,j]*(1-t) + Y[i,j+1]*t
                    verts.append((float(x0), float(y0), 0.0))

        if len(verts) < 2:
            self.report({'ERROR'}, get_text('no_curve_detected'))
            return {'CANCELLED'}

        self.create_curve_object("Courbe_Implicite", verts, context)
        self.report({'INFO'}, f"Courbe implicite créée ({len(verts)} segments)")
        return {'FINISHED'}

# Classes à enregistrer
classes: Tuple[type, ...] = (
    PLAN_CURVES_OT_refresh_presets,
    PLAN_CURVES_OT_load_preset_simple,
    PLAN_CURVES_OT_create_preset_simple,
    PLAN_CURVES_OT_delete_preset_simple,
    PLAN_CURVES_OT_validate_params,
    PLAN_CURVES_OT_generate_curve,
)

def register() -> None:
    """Enregistre les classes du module operators."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister() -> None:
    """Désenregistre les classes du module operators."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

