# ===============================================
# FICHIER: panels.py (Panneaux de l'interface avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    from bpy.types import Context, UILayout

import bpy
from bpy.types import Panel

from .preset_manager import SimplePresetManager, PresetData
from .preferences import get_text, SYMPY_AVAILABLE

class PLAN_CURVES_PT_main(Panel):
    """Panneau principal avec annotations complètes."""

    bl_label: str = "Courbes du Plan"
    bl_idname: str = "PLAN_CURVES_PT_main"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = "Courbes"

    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        props = context.scene.plan_curves_props

        # Vérification SymPy
        if not SYMPY_AVAILABLE:
            warning_box: UILayout = layout.box()
            warning_box.alert = True
            warning_box.label(text=get_text('sympy_not_installed'), icon='ERROR')
            warning_box.label(text=get_text('sympy_required'))
            warning_box.operator("screen.userpref_show",
                                text="Ouvrir les Préférences",
                                icon='PREFERENCES')
            layout.separator()

        # Type de courbe
        layout.prop(props, "curve_type", text=get_text('curve_type'))

        # Équations
        eq_box: UILayout = layout.box()
        eq_box.label(text=get_text('equations'), icon='SYNTAX_ON')

        equation_configs = {
            'EXPLICIT': [("y =", "equation1")],
            'PARAMETRIC': [("x(t) =", "equation1"), ("y(t) =", "equation2")],
            'POLAR': [("r(θ) =", "equation1")],
            'IMPLICIT': [("F(x,y) = 0", "equation1")]
        }

        if props.curve_type in equation_configs:
            for label, prop_name in equation_configs[props.curve_type]:
                eq_box.prop(props, prop_name, text=label)

        # Paramètres
        self._draw_parameters_section(layout, props)

        # Validation
        self._draw_validation_section(layout, props)

        # Génération
        self._draw_generation_section(layout)

        # === BOUTON NETTOYAGE DE SCÈNE (NOUVEAU) ===
        layout.separator()
        layout.operator("plan_curves.clean_scene", icon='TRASH')

    def _draw_parameters_section(self, layout: UILayout, props) -> None:
        param_box: UILayout = layout.box()
        param_box.label(text=get_text('parameters'), icon='SETTINGS')

        if props.curve_type in ['EXPLICIT', 'IMPLICIT']:
            col: UILayout = param_box.column(align=True)
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

    def _draw_validation_section(self, layout: UILayout, props) -> None:
        val_box: UILayout = layout.box()
        val_box.label(text=get_text('validation'), icon='CHECKMARK')
        val_box.operator("plan_curves.validate_params",
                        text=get_text('validate'),
                        icon='FILE_REFRESH')

        if props.validation_message:
            msg_box: UILayout = val_box.box()
            message_lower: str = props.validation_message.lower()

            if "valide" in message_lower or "valid" in message_lower:
                msg_box.label(text=props.validation_message, icon='CHECKMARK')
            else:
                msg_box.label(text=props.validation_message, icon='ERROR')

    def _draw_generation_section(self, layout: UILayout) -> None:
        layout.separator()
        row: UILayout = layout.row()
        row.scale_y = 1.5
        row.enabled = SYMPY_AVAILABLE  # Désactiver si SymPy n'est pas disponible
        row.operator("plan_curves.generate_curve",
                    text=get_text('generate_curve'),
                    icon='CURVE_DATA')


class PLAN_CURVES_PT_presets(Panel):
    """Panneau des presets avec annotations complètes."""

    bl_label: str = get_text('presets')
    bl_idname: str = "PLAN_CURVES_PT_presets"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = "Courbes"
    bl_options: set = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        props = context.scene.plan_curves_props

        # Navigation
        nav_box: UILayout = layout.box()
        nav_box.label(text=get_text('navigation'), icon='FILEBROWSER')

        # Liste des presets
        manager: SimplePresetManager = SimplePresetManager()
        preset_names: List[str] = manager.get_preset_names(props.curve_type)

        if preset_names:
            self._draw_preset_list(nav_box, preset_names, props.curve_type, manager)
        else:
            nav_box.label(text=get_text('no_presets'))

        # Rafraîchir
        nav_box.operator("plan_curves.refresh_presets",
                        text=get_text('refresh'),
                        icon='FILE_REFRESH')

        # Détails du preset sélectionné
        if props.selected_preset != "NONE" and props.show_preset_details:
            self.draw_preset_details(nav_box, props, manager)

        # Création de preset
        self._draw_preset_creation_section(layout, props)

        # Messages
        self._draw_messages_section(layout, props)

    def _draw_preset_list(self, parent: UILayout, preset_names: List[str],
                         curve_type: str, manager: SimplePresetManager) -> None:
        col: UILayout = parent.column(align=True)
        for name in preset_names:
            row: UILayout = col.row(align=True)
            op = row.operator("plan_curves.load_preset_simple",
                            text=name, icon='IMPORT')
            op.preset_name = name
            preset_data: Optional[PresetData] = manager.get_preset_by_name(curve_type, name)
            if preset_data and preset_data.get('editable', False):
                op_del = row.operator("plan_curves.delete_preset_simple",
                                    text="", icon='TRASH')
                op_del.preset_name = name

    def _draw_preset_creation_section(self, layout: UILayout, props) -> None:
        layout.separator()
        create_box: UILayout = layout.box()
        create_box.label(text=get_text('create_preset'), icon='PLUS')
        create_box.prop(props, "new_preset_name", text=get_text('preset_name'))
        create_box.prop(props, "new_preset_description", text=get_text('description'))
        create_box.operator("plan_curves.create_preset_simple", text=get_text('create_preset'), icon='FILE_NEW')

    def _draw_messages_section(self, layout: UILayout, props) -> None:
        if props.preset_message:
            msg_box: UILayout = layout.box()
            if "✓" in props.preset_message:
                msg_box.label(text=props.preset_message, icon='CHECKMARK')
            else:
                msg_box.label(text=props.preset_message, icon='ERROR')

    def draw_preset_details(self, parent_layout: UILayout, props,
                           manager: SimplePresetManager) -> None:
        try:
            preset_data: Optional[PresetData] = manager.get_preset_by_name(
                props.curve_type, props.selected_preset
            )

            if preset_data:
                details_box: UILayout = parent_layout.box()
                details_box.label(text=get_text('details'), icon='INFO')
                details_box.label(text=f"Nom: {props.selected_preset}")

                if 'description' in preset_data:
                    desc: str = preset_data['description']
                    details_box.label(text=f"{get_text('description')}: {desc}")

                if 'equation1' in preset_data:
                    eq: str = preset_data['equation1']
                    if len(eq) > 30:
                        eq = eq[:30] + "..."
                    details_box.label(text=f"{get_text('equation')} {eq}")

                source: str = (get_text('default_source')
                             if preset_data.get('source') == 'default'
                             else get_text('user_source'))
                details_box.label(text=f"{get_text('source')} {source}")

        except Exception as e:
            print(f"Erreur détails preset: {e}")

# Classes à enregistrer
classes: Tuple[type, ...] = (
    PLAN_CURVES_PT_main,
    PLAN_CURVES_PT_presets,
)

def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
