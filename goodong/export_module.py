import io
from typing import Set
import bpy
from bpy.types import Context, Event
import requests
from datetime import datetime
from tempfile import TemporaryDirectory
from .utils import close_panel

id = ""
pwd = ""
title = ""
description = ""
token  = ""
evnt = None

class ExportOperator(bpy.types.Operator):
    bl_idname = "object.export_operator"
    bl_label = "goodong"

    def execute(self, context):
        bpy.ops.screen.login('INVOKE_DEFAULT')
        return {'FINISHED'}
    
def update_event(self, event):
    global evnt
    evnt = event
    
def update_login_info(self, context):
    global id
    id = self.login_username
    global pwd
    pwd = self.login_password

def update_repo_info(self, context):
    global title
    global description
    title = self.title
    description = self.description


class LoginOperator(bpy.types.Operator):
    bl_idname = "screen.login"
    bl_label = "login"

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
        layout.operator("screen.login_button", text="Login")  

class LoginButtonOperator(bpy.types.Operator):
    bl_idname = "screen.login_button"
    bl_label = "login_button"

    def execute(self, context):
        login_operator = context.window_manager.operator_properties_last("screen.login")
        
        
        if login_operator:
            global id, pwd,token
            username = id
            password = pwd
            url = "http://localhost:8000/login" # 추후 배포시 url 변경해야함.
            payload = {"username" :username , "password" : password}
            response = requests.post(url, json=payload)
            token = response.headers['Authorization']
            if(response.status_code == 200):
                print("login success")
                bpy.ops.screen.create_repo('INVOKE_DEFAULT')
                return {'FINISHED'}
            else :
                self.report({'ERROR'}, "Login Failed.")
                return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Login Failed.")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)

class CreateRepoOperator(bpy.types.Operator):
    bl_idname = "screen.create_repo"
    bl_label = "Create Repository"
    
    title: bpy.props.StringProperty(name = "title", update=update_repo_info)
    description: bpy.props.StringProperty(name="description" , update=update_repo_info)
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the title and description:")
        layout.prop(self, "title")
        layout.prop(self, "description")
        layout.operator("screen.create_button", text="Create")  


class CreateButtonOperator(bpy.types.Operator):
    bl_idname = "screen.create_button"
    bl_label = "Create Button"
    
    def execute(self, context) :
        
        global id, title, description, evnt,token
        upload_date = datetime.utcnow().isoformat() + 'Z'
        print(upload_date)
        with TemporaryDirectory() as temp_dir :
            print(temp_dir)
            bpy.ops.export_scene.gltf(export_format='GLB', filepath= temp_dir + "/model.glb")
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = temp_dir + "/model.png"
            bpy.ops.render.render(write_still=True) 

            with open(temp_dir +"/model.glb", 'rb') as glb_file:
                glb_data = glb_file.read()
            with open(temp_dir +"/model.png", 'rb') as glb_file2:
                glb_data2 = glb_file2.read()
        
        files = {'file': ('model.glb', glb_data)}
        file2 = {'png_file': ('model.png',glb_data2), 'file': ('model.glb', glb_data)}
        
        if title == "" and description == "":
            payload = {"userId" : id , "uploadDate": upload_date}
            url = "http://localhost:8000/ai/test"

            response = requests.post(url=url, data=payload, files= file2, headers={"Authorization": token})
            
            if response._content.decode() == 'success':

                self.report({'INFO'}, "create repository suceess.")
                close_panel(evnt)
                
            else :
                self.report({'ERROR'}, "failed to create repository")
            
            return {'FINISHED'}
        else :
            payload = {"title": title, "content": description ,"userId" : id , "uploadDate": upload_date}
            url = "http://localhost:8000/repository/savepost"
            response = requests.post(url=url, data=payload, files= files, headers={"Authorization": token})
            
            if response._content.decode() == 'success':

                self.report({'INFO'}, "create repository suceess.")
                close_panel(evnt)
                
            else :
                self.report({'ERROR'}, "failed to create repository")
            
            return {'FINISHED'}
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)
    
