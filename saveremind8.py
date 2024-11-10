bl_info = {
    "name": "Save Reminder",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound reminder to save your work at customizable intervals",
    "category": "System",
}

import bpy
import aud
import os
import time
from bpy.props import IntProperty, StringProperty, BoolProperty
from bpy.types import AddonPreferences, Operator
from pathlib import Path

class SaveReminderPreferences(AddonPreferences):
    bl_idname = __name__

    # Preferences properties
    interval: IntProperty(
        name="Reminder Interval (minutes)",
        description="Time between save reminders",
        default=15,
        min=1,
        max=120
    )
    
    sound_file: StringProperty(
        name="Sound File",
        description="Path to the sound file for the reminder",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    enabled: BoolProperty(
        name="Enable Save Reminder",
        description="Toggle save reminder on/off",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enabled")
        layout.prop(self, "interval")
        layout.prop(self, "sound_file")

class SAVREM_OT_play_reminder(Operator):
    bl_idname = "savrem.play_reminder"
    bl_label = "Save Reminder"
    bl_description = "Reminder to save your work"
    
    def execute(self, context):
        preferences = context.preferences.addons[__name__].preferences
        
        # Check if file is unsaved
        if not bpy.data.is_saved:
            # Play sound if sound file is set
            if preferences.sound_file and os.path.exists(preferences.sound_file):
                device = aud.Device()
                sound = aud.Sound(preferences.sound_file)
                device.play(sound)
            
            self.report({'WARNING'}, "Please save your work!")
        
        return {'FINISHED'}

class SaveReminderTimer:
    _timer = None
    _last_check = 0
    
    @classmethod
    def start(cls):
        if cls._timer is not None:
            return
        
        cls._last_check = time.time()
        cls._timer = bpy.app.timers.register(cls.check_save_status, persistent=True)
    
    @classmethod
    def stop(cls):
        if cls._timer is not None:
            bpy.app.timers.unregister(cls._timer)
            cls._timer = None
    
    @classmethod
    def check_save_status(cls):
        preferences = bpy.context.preferences.addons[__name__].preferences
        
        if not preferences.enabled:
            cls.stop()
            return None
        
        current_time = time.time()
        if current_time - cls._last_check >= preferences.interval * 60:
            cls._last_check = current_time
            bpy.ops.savrem.play_reminder()
        
        return 1.0  # Check every second

def register():
    bpy.utils.register_class(SaveReminderPreferences)
    bpy.utils.register_class(SAVREM_OT_play_reminder)
    SaveReminderTimer.start()

def unregister():
    SaveReminderTimer.stop()
    bpy.utils.unregister_class(SAVREM_OT_play_reminder)
    bpy.utils.unregister_class(SaveReminderPreferences)

if __name__ == "__main__":
    register()