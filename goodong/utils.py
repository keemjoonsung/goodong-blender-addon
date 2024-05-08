import bpy


def close_panel(event):
    x, y = event.mouse_x, event.mouse_y
    bpy.context.window.cursor_warp(10, 10)

    def move_back():
        bpy.context.window.cursor_warp(x, y)
        
    bpy.app.timers.register(move_back, first_interval=0.1)
