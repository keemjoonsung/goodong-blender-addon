import json
import io,os
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
nickname = ""
token  = ""
evnt = None
posts_data = []
items = []
id_map= {}
selected_title_global = ""
tag=[]

visibility = "PUBLIC"
addon_folder = os.path.join(os.path.expanduser("~"), ".goodong_blender_addon")  # 폴더 이름에 .을 추가하여 숨김 처리
os.makedirs(addon_folder, exist_ok=True)  # 폴더가 없으면 생성
TOKEN_FILE = os.path.join(addon_folder, "goodong_auth.json")  # 파일 이름을 .token.json으로 설정

class ExportOperator(bpy.types.Operator):
    bl_idname = "object.export_operator"
    bl_label = "goodong"
    
    def execute(self, context):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as file:
                global token
                token_data = json.load(file)
                token = "Bearer " + token_data.get('token')
                print(f"Loaded token: {token}")
                url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/auth/check-token"
                headers = {"Authorization": token}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    global posts_data, id_map, nickname
                    nickname = response.json()['data']['nickname']
                    url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts?all=true"
                    posts_response = requests.get(url, headers=headers)
                    if(posts_response.status_code == 200) :
                        posts_data = posts_response.json()['data']['content']
                        id_map = {item['title']: item['postId'] for item in posts_data}
                        bpy.ops.screen.show_titles_operator('INVOKE_DEFAULT')
                    else:
                        os.remove(TOKEN_FILE)
                        token = ""
                        nickname = ""
                        self.report({'ERROR'}, "Load repository failed.")
                        return {'FINISHED'}                
                else :
                    os.remove(TOKEN_FILE)
                    token = ""
                    bpy.ops.screen.login('INVOKE_DEFAULT')
        else:
            bpy.ops.screen.login('INVOKE_DEFAULT')
        
        return {'FINISHED'}
    
def update_event(self, event):
    global evnt
    evnt = event

def init_global():
    global title, description,commit_msg,tag_1,tag_2,tag_3,tag,posts_data
    title = ""
    description=""
    commit_msg=""
    tag =[]
    posts_data=[]
    
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
    if self.title != "":
        title = self.title
    if self.description != "" :
        description = self.description
    tag = []
    if self.tag_1 != "":
        tag.append(self.tag_1)
    if self.tag_2 != "":
        tag.append(self.tag_2)
    if self.tag_3 != "":
        tag.append(self.tag_3)
    visibility = str(self.visibility)
    print("변경 : ")
    print(title, description,tag,visibility)

def update_tag(self, context):
    global tag
    tag = []
    if self.tag_1 != "":
        tag.append(self.tag_1)
    if self.tag_2 != "":
        tag.append(self.tag_2)
    if self.tag_3 != "":
        tag.append(self.tag_3)
def update_commit_msg(self, context):
    global commit_msg
    commit_msg = self.commit_msg

def update_visibility(self, context):
    global visibility
    visibility = self.visibility
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

            if(response.status_code == 200):
                token = response.json()['data']
                token_data = {"token": token}
                with open(TOKEN_FILE, 'w') as file:
                    json.dump(token_data, file)
                token = "Bearer " + token
                posts_url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts?all=true"  # Change URL as needed.
                headers = {"Authorization": token}
                posts_response = requests.get(posts_url, headers=headers)
                if posts_response.status_code == 200:
                    posts_data = posts_response.json()['data']['content']
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

    def execute(self, context):
        # my_tool의 값들을 확인하거나 사용할 수 있습니다
        props = context.scene.my_tool
        print(f"Title: {props.title}, Description: {props.description}, Tags: {props.tag_1}, {props.tag_2}, {props.tag_3}")
        # 필요에 따라 서버에 전송하거나 로직 처리
        return {'FINISHED'}

    def invoke(self, context, event):
        # 초기화: my_tool의 값을 초기화하거나 기본값 설정
        props = context.scene.my_tool
        props.title = ""
        props.description = ""
        props.tag_1 = ""
        props.tag_2 = ""
        props.tag_3 = ""
        
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the title and description:")
        
        # my_tool의 속성들을 바로 참조해서 입력 UI 필드를 구성
        props = context.scene.my_tool
        layout.prop(props, "title")
        layout.prop(props, "description")
        
        row = layout.row()
        row.prop(props, "tag_1", text="Tag 1")
        row.prop(props, "tag_2", text="Tag 2")
        row.prop(props, "tag_3", text="Tag 3")
        
        layout.prop(props, "visibility", expand=True)
        layout.operator("screen.ai_button", text="AI Create")  
        layout.operator("screen.create_button", text="Create")  
    

class CreateButtonOperator(bpy.types.Operator):
    bl_idname = "screen.create_button"
    bl_label = "Create Button"
    
    def execute(self, context) :
        
        global id, title, description, evnt,token,tag,visibility,tag
        with TemporaryDirectory() as temp_dir :
            bpy.ops.export_scene.gltf(export_format='GLB', filepath= temp_dir + "/model.glb")
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = temp_dir + "/model.png"
            bpy.ops.render.render(write_still=True) 

            with open(temp_dir +"/model.glb", 'rb') as glb_file:
                glb_data = glb_file.read()        
        files = {'fileGlb': ('model.glb', glb_data)}
        
        
        payload = {"title": title, "content": description ,"status" : visibility, "tags" :tag }
        url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts"
        response = requests.post(url=url, data=payload, files= files, headers={"Authorization": token})
            
        if response.status_code == 200:
            self.report({'INFO'}, "create repository suceess.")

            title=""
            description=""
            tag = []
            close_panel(evnt)
        else :
            self.report({'ERROR'}, "Duplicated title, please change your title.")

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
            return [(str(post['postId']), post['title'], "") for post in posts_data]
        else:
            return [('', 'No Posts Available', '')]
    @staticmethod
    def update_selected_title(self):
        global selected_title_global
        selected_title_global = self.selected_title
        
    def execute(self, context):
        bpy.ops.screen.confirm_selection_operator('INVOKE_DEFAULT', selected_title=self.selected_title)
        return {'FINISHED'}

    def invoke(self, context, event):
        global selected_title_global
        wm = context.window_manager
        selected_title_global = self.selected_title
        return wm.invoke_popup(self)

    
    def draw(self, context):
        
        global nickname
        layout = self.layout
        layout.label(text=f"Select {nickname}'s Repository:")
        layout.prop(self, "selected_title", text="")
        
        layout.separator()  
        split = layout.split(factor=0.5)

        col = split.column()
        col.operator("screen.create_repo", text="New Repository", icon='PLUS')

        col = split.column()
        col.operator("screen.next_operator", text="Commit", icon='FORWARD')
        
        col = split.column()
        col.operator("screen.logout_operator", text="Logout", icon='QUIT')

class LogoutOperator(bpy.types.Operator):
    bl_idname = "screen.logout_operator"
    bl_label = "Logout"
    
    def execute(self, context) :
        global token
        token = ""
        os.remove(TOKEN_FILE)
        self.report({'INFO'}, "Logout success")
        return {'FINISHED'}
    
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

    commit_msg: bpy.props.StringProperty(name="Commit Msg",update = update_commit_msg)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "commit_msg")
        self.layout.operator("screen.commit_button", text="Commit and Push")  


    def invoke(self, context, event):
        commit_msg = ""
        wm = context.window_manager
        return wm.invoke_popup(self)

        
class AiButtonOperator(bpy.types.Operator):
    bl_idname = "screen.ai_button"
    bl_label = "Commit Button"
    
    def execute(self, context) :
        
        global id, title, description, evnt,token,visibility
        with TemporaryDirectory() as temp_dir :
            bpy.ops.export_scene.gltf(export_format='GLB', filepath= temp_dir + "/model.glb")
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = temp_dir + "/model.png"
            bpy.ops.render.render(write_still=True) 

            with open(temp_dir +"/model.png", 'rb') as glb_file2:
                glb_data2 = glb_file2.read()
            with open(temp_dir +"/model.glb", 'rb') as glb_file:
                glb_data = glb_file.read()        

        # file2 = {'fileGlb': ('model.glb',glb_data), "filePng" : ('model.png',glb_data2)}
        # payload = {'status': visibility}
        file2 = {"filePng" : ('model.png',glb_data2) }
        url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts/metadata"
        response = requests.post(url=url, files= file2 ,headers={"Authorization": token})
            
        if response.status_code == 200:
            data = response.json()['data']
            title = data['title']
            description = data['content']
            tags = data['tags']
            print(title,description,tag)
            context.scene.my_tool.title = title
            context.scene.my_tool.description = description
            if len(tags) == 3:
                context.scene.my_tool.tag_1 = tags[0]
                context.scene.my_tool.tag_2 = tags[1]
                context.scene.my_tool.tag_3 = tags[2]
            context.scene.update_tag()
            
            self.report({'INFO'}, "ai create success.")
            print(response.json()['data'])                
        else :
            self.report({'ERROR'}, "failed to generate metadata of your model.")
            
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)

class MyProperties(bpy.types.PropertyGroup):
    title: bpy.props.StringProperty(name="title", update = update_repo_info)
    description: bpy.props.StringProperty(name="description", update = update_repo_info)
    tag_1: bpy.props.StringProperty(name="tag 1", update = update_repo_info)
    tag_2: bpy.props.StringProperty(name="tag 2", update = update_repo_info)
    tag_3: bpy.props.StringProperty(name="tag 3", update = update_repo_info)
    visibility: bpy.props.EnumProperty(
        name="Visibility",
        description="Select visibility",
        items=[
            ('PRIVATE', "Private", "This is a private post"),
            ('PUBLIC', "Public", "This is a public post")
        ],
        default='PUBLIC',  # Default to 'Public'
        update=update_visibility  # 변경 시 함수 호출
    )

class CommitButtonOperator(bpy.types.Operator):
    bl_idname = "screen.commit_button"
    bl_label = "commit_button"

    def execute(self, context):
        global selected_title_global, commit_msg,evnt

        with TemporaryDirectory() as temp_dir :
            bpy.ops.export_scene.gltf(export_format='GLB', filepath= temp_dir + "/model.glb")
            with open(temp_dir +"/model.glb", 'rb') as glb_file:
                glb_data = glb_file.read()        

        file = {'fileGlb': ('model.glb',glb_data)}
        url = "https://goodong-api-741693435028.asia-northeast1.run.app/api/posts/"+ selected_title_global# 추후 배포시 url 변경해야함.
        headers = {"Authorization": token}
        
        payload = {"commitMessage" :commit_msg}
        response = requests.patch(url, data=payload, files=file,headers=headers)
        commit_msg = ""
        if response.status_code == 200:
            self.report({'INFO'}, "Commit and Push success.")
                
        else: 
            self.report({'ERROR'}, "Failed to Commit")
        init_global()
        close_panel(evnt)
        return {'FINISHED'}

    
    def invoke(self, context, event):
        update_event(self, event=event)
        return self.execute(context)
