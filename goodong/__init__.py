import io
from typing import Set
import bpy
from bpy.types import Context, Event
import requests
from datetime import datetime
from tempfile import TemporaryDirectory
from . import export_module
from . import import_module
bl_info = {
    "name": "goodong",
    "author": "Kim Joon Sung",
    "description": "Sample addon for goodong",
    "blender": (2, 93, 0),
    "version": (0, 0, 1),
    "location": "File > Import-Export",
    "warning": "",
    "category": ""
}

def menu_func_export(self, context):
    self.layout.operator(export_module.ExportOperator.bl_idname)

def menu_func_import(self, context):
    self.layout.operator(import_module.ImportOperator.bl_idname)


def register():
    bpy.utils.register_class(export_module.ExportOperator)
    bpy.utils.register_class(import_module.ImportOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    bpy.utils.register_class(export_module.LoginOperator)
    bpy.utils.register_class(export_module.LoginButtonOperator)
    bpy.utils.register_class(export_module.CreateRepoOperator)
    bpy.utils.register_class(export_module.CreateButtonOperator)
    
    bpy.utils.register_class(import_module.URLInputOperator)
    bpy.utils.register_class(import_module.NetworkOperator)
    bpy.types.TOPBAR_MT_file.append(menu_func_login)

def unregister():
    bpy.utils.unregister_class(export_module.ExportOperator)
    bpy.utils.unregister_clasS(import_module.ImportOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    bpy.utils.unregister_class(export_module.LoginOperator)
    bpy.utils.unregister_class(export_module.LoginButtonOperator)
    bpy.utils.unregister_class(export_module.CreateRepoOperator)
    bpy.utils.unregister_class(export_module.CreateButtonOperator)

    bpy.utils.unregister_class(import_module.URLInputOperator)
    bpy.utils.unregister_class(import_module.NetworkOperator)
    bpy.types.TOPBAR_MT_file.remove(menu_func_login)


def menu_func_login(self, context):
    layout = self.layout

if __name__ == "__main__":
    register()
