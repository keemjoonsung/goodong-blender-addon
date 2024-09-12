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
commit_msg = ""
token  = ""
evnt = None
posts_data = []
items = []
id_map= {}
selected_title_global = ""
tag=[]
visibility = "PUBLIC"
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
    global tag
    global visibility
    
    title = self.title
    description = self.description
    if self.tag_1 != "":
        tag.append(self.tag_1)
    if self.tag_2 != "":
        tag.append(self.tag_2)
    if self.tag_3 != "":
        tag.append(self.tag_3)
    visibility = str(self.visibility)

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
            global id, pwd,token, posts_data ,items,id_map
            username = id
            password = pwd
            url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/auth/login" # 추후 배포시 url 변경해야함.
            payload = {"email" :username , "password" : password}
            response = requests.post(url, json=payload)
            token = response.json()['data']
            token = "Bearer " + token
            print(token)
            if(response.status_code == 200):
                print("login success")
                # bpy.ops.screen.create_repo('INVOKE_DEFAULT')
                posts_url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts"  # Change URL as needed.
                headers = {"Authorization": token}
                posts_response = requests.get(posts_url, headers=headers)
                if posts_response.status_code == 200:
                    posts_data = posts_response.json()['data']
                    id_map = {item['title']: item['postId'] for item in posts_data}
                    bpy.ops.screen.show_titles_operator('INVOKE_DEFAULT')
                    
            
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
    commit_msg: bpy.props.StringProperty(name="commit msg" , update=update_repo_info)
    tag_1 : bpy.props.StringProperty(name="tag 1" , update=update_repo_info)
    tag_2 : bpy.props.StringProperty(name="tag 2" , update=update_repo_info)
    tag_3 : bpy.props.StringProperty(name="tag 3" , update=update_repo_info)
    visibility: bpy.props.EnumProperty(
        name="Visibility",
        description="Select visibility",
        items=[
            ('PRIVATE', "Private", "This is a private post"),
            ('PUBLIC', "Public", "This is a public post")
        ],
        default='PUBLIC',  # Default to 'Public'
        update=update_repo_info  # Optional: trigger an update function if needed
    )
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
        row = layout.row()
        row.prop(self, "tag_1", text="Tag 1")
        row.prop(self, "tag_2", text="Tag 2")
        row.prop(self, "tag_3", text="Tag 3")
        layout.prop(self, "visibility", expand=True)
        layout.operator("screen.ai_button", text="AI Create")  
        layout.operator("screen.create_button", text="Create")  
    

class CreateButtonOperator(bpy.types.Operator):
    bl_idname = "screen.create_button"
    bl_label = "Create Button"
    
    def execute(self, context) :
        
        global id, title, description, evnt,token,tag,visibility,tag
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
        files = {'file': ('model.glb', glb_data)}
        
        
        payload = {"title": title, "content": description ,"status" : visibility, "tags" :tag }
        url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts"
        response = requests.post(url=url, data=payload, files= files, headers={"Authorization": token})
            
        if response.status_code == 200:
            self.report({'INFO'}, "create repository suceess.")
            tag = []
            close_panel(evnt)
        else :
            self.report({'ERROR'}, "failed to create repository")
            tag =[]
        return {'FINISHED'}
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)
    
    
class ShowTitlesOperator(bpy.types.Operator):
    bl_idname = "screen.show_titles_operator"
    bl_label = "Select Post Title"

    # EnumProperty that dynamically fetches items via a static method
    selected_title: bpy.props.EnumProperty(items=lambda self, context: ShowTitlesOperator.get_items(),update=lambda self, context: ShowTitlesOperator.update_selected_title(self))

    @staticmethod
    def get_items():
        global posts_data
        if posts_data:
            # Create the items dynamically from posts_data
            return [(str(post['postId']), post['title'], "") for post in posts_data]
        else:
            # Fallback item if no posts are available
            return [('', 'No Posts Available', '')]
    @staticmethod
    def update_selected_title(self):
        global selected_title_global
        # 전역 변수에 선택된 title 저장
        selected_title_global = self.selected_title
        print(f"Updated selected title: {selected_title_global}")
        
    def execute(self, context):
        print(f"Selected title: {self.selected_title}")
        bpy.ops.screen.confirm_selection_operator('INVOKE_DEFAULT', selected_title=self.selected_title)
        return {'FINISHED'}

    def invoke(self, context, event):
        global selected_title_global
        wm = context.window_manager
        selected_title_global = self.selected_title
        return wm.invoke_popup(self)

    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select Your Repository:")
        # Display the drop-down menu with dynamic items
    # Display the drop-down menu with dynamic items
        layout.prop(self, "selected_title", text="")
        
        layout.separator()  # Adds a line separator for better UI layout

        # Split the layout into two columns
        split = layout.split(factor=0.5)

        # Add the "Create" button in the first half
        col = split.column()
        col.operator("screen.create_repo", text="Create", icon='PLUS')

        # Add the "Next" button in the second half
        col = split.column()
        col.operator("screen.next_operator", text="Next", icon='FORWARD')

    
class TitleSelectedOperator(bpy.types.Operator):
    bl_idname = "screen.title_selected"
    bl_label = "Title Selected"

    title: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.screen.confirm_selection_operator('INVOKE_DEFAULT', selected_title=self.title)
        return {'FINISHED'}

class NextOperator(bpy.types.Operator):
    bl_idname = "screen.next_operator"
    bl_label = "Commit Changes"

    commit_message: bpy.props.StringProperty(name="Commit Msg")

    def execute(self, context):
        print(f"Commit Message: {self.commit_message}")
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "commit_message")
        self.layout.operator("screen.login_button", text="Commit")  



    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class CommitRepoOperator(bpy.types.Operator):
    bl_idname = "screen.create_repo"
    bl_label = "Create Repository"
    
    commit_msg: bpy.props.StringProperty(name="commit msg" , update=update_repo_info)
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter Commit Message:")
        layout.prop(self, "commit_msg")
        layout.operator("screen.commit_button", text="Commit") 
        

class AiButtonOperator(bpy.types.Operator):
    bl_idname = "screen.ai_button"
    bl_label = "Commit Button"
    
    def execute(self, context) :
        
        global id, title, description, evnt,token,tag,visibility
        upload_date = datetime.utcnow().isoformat() + 'Z'
        print(upload_date)
        with TemporaryDirectory() as temp_dir :
            bpy.ops.export_scene.gltf(export_format='GLB', filepath= temp_dir + "/model.glb")
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = temp_dir + "/model.png"
            bpy.ops.render.render(write_still=True) 

            with open(temp_dir +"/model.png", 'rb') as glb_file2:
                glb_data2 = glb_file2.read()
            with open(temp_dir +"/model.glb", 'rb') as glb_file:
                glb_data = glb_file.read()        

        file2 = {'fileGlb': ('model.glb',glb_data), "file" : ('model.png',glb_data2)}
        url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/ai?autoCreate=true&status=" + visibility
        print(url)
        response = requests.post(url=url, files= file2, headers={"Authorization": token})
            
        if response.status_code == 200:
            print(response.json())
            self.report({'INFO'}, "ai create success.")
    
            close_panel(evnt)
                
        else :
            self.report({'ERROR'}, "failed to create (Maybe duplicated title)")
            
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)