import os
import bpy
from io import BytesIO
from .utils import close_panel
import requests
from tempfile import TemporaryDirectory

fileName = ""
id = ""
pwd = ""
token = ""
evnt = None

def update_event(self, event):
    global evnt
    evnt = event

def update_url(self, context):
    global fileName
    fileName = self.url_input

def update_login_info(self, context):
    global id
    id = self.login_username
    global pwd
    pwd = self.login_password

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
        global fileName
        
        getUrl = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts/models?fileName=" + fileName
        response = requests.get(getUrl)
        if response.status_code == 200 :
            with TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, "model.glb")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                bpy.ops.import_scene.gltf(filepath=file_path)
            
            self.report({'INFO'}, "import success.")
        elif response.status_code == 401 :
            bpy.ops.screen.auth('INVOKE_DEFAULT')
            return {'FINISHED'}
        else :
            self.report({'ERROR'}, "import failed. Please check your code.")
            return {'FINISHED'}
        fileName = ""
        close_panel(evnt)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)


class AuthOperator(bpy.types.Operator):
    bl_idname = "screen.auth"
    bl_label = "auth"

    login_username: bpy.props.StringProperty(name="Email", update=update_login_info)
    login_password: bpy.props.StringProperty(name="Password", subtype='PASSWORD', update=update_login_info)

    def execute(self, context):
        global pwd
        pwd = ""
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Login goodong")
        layout.prop(self, "login_username")
        layout.prop(self, "login_password")
        layout.operator("screen.auth_button", text="Login")  

class AuthButtonOperator(bpy.types.Operator):
    bl_idname = "screen.auth_button"
    bl_label = "auth_button"

    def execute(self, context):
        login_operator = context.window_manager.operator_properties_last("screen.login")
        
        
        if login_operator:
            global id, pwd,fileName,token
            username = id
            password = pwd
            url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/auth/login" # 추후 배포시 url 변경해야함.
            payload = {"email" :username , "password" : password}
            response = requests.post(url, json=payload)
            if(response.status_code == 200):
                token = "Bearer " + response.json()['data']
                getUrl = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts/models?fileName=" + fileName
                headers = {"Authorization": token}
                response = requests.get(getUrl,headers=headers)
                if response.status_code == 200 :
                    with TemporaryDirectory() as temp_dir:
                        file_path = os.path.join(temp_dir, "model.glb")
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        bpy.ops.import_scene.gltf(filepath=file_path)
                    self.report({'INFO'}, "import success.")
                    return {'FINISHED'}
                else :
                    self.report({'ERROR'}, "Import Failed.")
                    return {'FINISHED'}                    
            else :
                self.report({'ERROR'}, "Login Failed.")
                return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Unexpected Error.")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)