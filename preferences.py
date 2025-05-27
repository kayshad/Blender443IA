# ===============================================
# FICHIER: preferences.py (Gestion des préférences avec annotations)
# ===============================================

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Set, Union

if TYPE_CHECKING:
    from typing import Any
    from bpy.types import Context, UILayout
    from bpy.types import AddonPreferences as BlenderAddonPreferences

import bpy
import subprocess
import sys
from bpy.types import AddonPreferences, Operator

from .translations import TRANSLATIONS

try:
    import sympy as sp
    SYMPY_AVAILABLE: bool = True
except ImportError:
    sp = None
    SYMPY_AVAILABLE = False

# Type aliases
LanguageCode = Union[str, str]  # 'fr' | 'en'

def get_addon_preferences() -> Optional[PLAN_CURVES_AddonPreferences]:
    """
    Récupère les préférences de l'addon de manière sécurisée.

    Returns:
        Les préférences de l'addon ou None si erreur
    """
    try:
        addon_name: str = __package__
        addon = bpy.context.preferences.addons.get(addon_name)
        if addon:
            return addon.preferences
        return None
    except (KeyError, AttributeError):
        return None

def get_text(key: str) -> str:
    """
    Récupère le texte traduit selon la langue sélectionnée.

    Args:
        key: Clé de traduction

    Returns:
        Texte traduit ou clé si non trouvé
    """
    try:
        prefs: Optional[PLAN_CURVES_AddonPreferences] = get_addon_preferences()
        if prefs and hasattr(prefs, 'language'):
            lang: LanguageCode = prefs.language
            return TRANSLATIONS.get(lang, TRANSLATIONS['fr']).get(key, key)
    except Exception:
        pass
    return TRANSLATIONS['fr'].get(key, key)

class PLAN_CURVES_AddonPreferences(AddonPreferences):
    """Préférences de l'addon avec gestion de la langue et SymPy."""

    bl_idname: str = __package__

    # === LANGUE ===
    language: bpy.props.EnumProperty(  # type: ignore
        name="Language",
        items=[
            ('fr', "Français", "Interface en français"),
            ('en', "English", "English interface"),
        ],
        default='fr',
        description="Langue de l'interface"
    )

    # === SYMPY ===
    sympy_check_done: bpy.props.BoolProperty(  # type: ignore
        name="SymPy Check Done",
        default=False,
        description="Indique si la vérification SymPy a été faite"
    )

    sympy_install_status: bpy.props.StringProperty(  # type: ignore
        name="SymPy Install Status",
        default="",
        description="Statut de l'installation SymPy"
    )

    def draw(self, context: Context) -> None:
        """
        Dessine l'interface des préférences.

        Args:
            context: Contexte Blender
        """
        layout: UILayout = self.layout

        # === SECTION LANGUE ===
        lang_box: UILayout = layout.box()
        lang_box.label(text=get_text('language'), icon='WORLD')
        lang_box.prop(self, "language", expand=True)

        layout.separator()

        # === SECTION SYMPY ===
        sympy_box: UILayout = layout.box()
        sympy_box.label(text=get_text('sympy_management'), icon='CONSOLE')

        # Statut SymPy
        status_row: UILayout = sympy_box.row()
        status_row.label(text=get_text('sympy_status'))

        if SYMPY_AVAILABLE:
            status_row.label(text=get_text('sympy_installed'), icon='CHECKMARK')
        else:
            status_row.label(text=get_text('sympy_not_installed_pref'), icon='ERROR')

        # Boutons
        buttons_row: UILayout = sympy_box.row(align=True)
        buttons_row.operator("plan_curves.check_sympy",
                           text=get_text('check_sympy'),
                           icon='FILE_REFRESH')

        if not SYMPY_AVAILABLE:
            buttons_row.operator("plan_curves.install_sympy",
                               text=get_text('install_sympy'),
                               icon='IMPORT')

        # Messages de statut
        if self.sympy_install_status:
            msg_box: UILayout = sympy_box.box()
            status_lower: str = self.sympy_install_status.lower()

            if "success" in status_lower or "succès" in status_lower:
                msg_box.label(text=self.sympy_install_status, icon='CHECKMARK')
                msg_box.label(text=get_text('restart_blender'), icon='INFO')
            elif "error" in status_lower or "erreur" in status_lower:
                msg_box.label(text=self.sympy_install_status, icon='ERROR')
            else:
                msg_box.label(text=self.sympy_install_status, icon='INFO')

class PLAN_CURVES_OT_check_sympy(Operator):
    """Vérifie le statut de SymPy."""

    bl_idname: str = "plan_curves.check_sympy"
    bl_label: str = "Check SymPy"
    bl_description: str = "Vérifie si SymPy est installé"

    def execute(self, context: Context) -> Set[str]:
        """
        Exécute la vérification de SymPy.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        global SYMPY_AVAILABLE, sp

        try:
            import importlib
            if sp is not None:
                importlib.reload(sp)
            else:
                import sympy as sp
            SYMPY_AVAILABLE = True

            prefs: Optional[PLAN_CURVES_AddonPreferences] = get_addon_preferences()
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

class PLAN_CURVES_OT_install_sympy(Operator):
    """Installe SymPy via pip."""

    bl_idname: str = "plan_curves.install_sympy"
    bl_label: str = "Install SymPy"
    bl_description: str = "Installe SymPy automatiquement"

    def execute(self, context: Context) -> Set[str]:
        """
        Exécute l'installation de SymPy.

        Args:
            context: Contexte Blender

        Returns:
            Statut d'exécution
        """
        prefs: Optional[PLAN_CURVES_AddonPreferences] = get_addon_preferences()
        if prefs:
            prefs.sympy_install_status = get_text('installing_sympy')

        try:
            python_exe: str = sys.executable

            result = subprocess.run([
                python_exe, "-m", "pip", "install", "sympy"
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                if prefs:
                    prefs.sympy_install_status = get_text('sympy_install_success')
                self.report({'INFO'}, get_text('sympy_install_success'))
                bpy.ops.plan_curves.check_sympy()
            else:
                error_msg: str = f"{get_text('sympy_install_error')}: {result.stderr}"
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

# Classes à enregistrer
classes: tuple[type, ...] = (
    PLAN_CURVES_AddonPreferences,
    PLAN_CURVES_OT_check_sympy,
    PLAN_CURVES_OT_install_sympy,
)

def register() -> None:
    """Enregistre les classes du module preferences."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister() -> None:
    """Désenregistre les classes du module preferences."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

