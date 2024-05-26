import os
import bpy
from io import BytesIO
from .utils import close_panel
import requests
from tempfile import TemporaryDirectory

url = ""
evnt = None

def update_event(self, event):
    global evnt
    evnt = event

def update_url(self, context):
    global url
    url = self.url_input
    print("url = " , url)
    
class ImportOperator(bpy.types.Operator):
    bl_idname = "object.import_operator"
    bl_label = "goodong"

    def execute(self, context):
        bpy.ops.screen.url_input('INVOKE_DEFAULT')
        return {'FINISHED'}

class URLInputOperator(bpy.types.Operator):
    bl_idname = "screen.url_input"
    bl_label = "url input"
    
    url_input: bpy.props.StringProperty(name="URL", update =update_url)

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Import from goodong.com")
        layout.prop(self, "url_input")
        layout.operator("screen.network", text="Import")  
        

class NetworkOperator(bpy.types.Operator):
    bl_idname = "screen.network"
    bl_label = "import button"

    def execute(self, context):
        global url
        
        getUrl = "http://localhost:8000/repository/download/" + url
        response = requests.get(getUrl)
        if response.status_code != 200 :
            self.report({'ERROR'}, "import failed. Please check your url.")
            return {'FINISHED'}
        
        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "model.glb")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            bpy.ops.import_scene.gltf(filepath=file_path)
        
        self.report({'INFO'}, "import success.")
        
        url = ""
        close_panel(evnt)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)



