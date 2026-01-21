bl_info = {
    "name": "Image Sequence to APNG",
    "author": "aecii 3d",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "Properties > Output",
    "description": "Export an image sequence as an animated PNG (APNG)",
    "category": "Render",
}

import bpy
import os
import struct
import zlib
from bpy.types import Operator, Panel
from bpy.props import StringProperty, IntProperty
from math import ceil

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# ------------------------------------------------------------
# Minimal APNG writer (pure Python, no dependencies)
# ------------------------------------------------------------

def png_chunk(chunk_type, data):
    return (
        struct.pack(">I", len(data)) +
        chunk_type +
        data +
        struct.pack(">I", zlib.crc32(chunk_type + data) & 0xffffffff)
    )

def write_apng(frames, output_path, fps):
    delay_num = 1000
    delay_den = int(1000 * fps)

    with open(output_path, "wb") as f:
        f.write(PNG_SIGNATURE)

        # Write IHDR from first frame
        ihdr, idat = extract_png_chunks(frames[0])
        f.write(ihdr)

        # acTL
        f.write(png_chunk(b"acTL", struct.pack(">II", len(frames), 0)))

        sequence = 0

        for i, frame in enumerate(frames):
            ihdr, idat = extract_png_chunks(frame)

            fcTL = struct.pack(
                ">IIIIIHHBB",
                sequence,
                *get_png_size(frame),
                0, 0,
                delay_num, delay_den,
                0, 0
            )
            f.write(png_chunk(b"fcTL", fcTL))
            sequence += 1

            if i == 0:
                f.write(idat)
            else:
                f.write(
                    png_chunk(
                        b"fdAT",
                        struct.pack(">I", sequence) + idat[8:-4]
                    )
                )
                sequence += 1

        f.write(png_chunk(b"IEND", b""))

def extract_png_chunks(path):
    with open(path, "rb") as f:
        data = f.read()

    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Invalid PNG file")

    pos = 8
    ihdr = None
    idat_data = b""

    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        chunk = data[pos:pos+12+length]

        if ctype == b"IHDR":
            ihdr = chunk
        elif ctype == b"IDAT":
            idat_data += chunk[8:-4]

        pos += 12 + length

    idat = png_chunk(b"IDAT", idat_data)
    return ihdr, idat

def get_png_size(path):
    with open(path, "rb") as f:
        f.seek(16)
        width, height = struct.unpack(">II", f.read(8))
    return width, height

# ------------------------------------------------------------
# Blender Operator
# ------------------------------------------------------------

class RENDER_OT_export_apng(Operator):
    bl_idname = "render.export_apng"
    bl_label = "Export APNG"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        input_dir = scene.apng_input_dir
        output_file = scene.apng_output_file
        fps = scene.apng_fps

        if not os.path.isdir(input_dir):
            self.report({'ERROR'}, "Invalid input directory")
            return {'CANCELLED'}

        frames = sorted(
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith(".png")
        )

        if not frames:
            self.report({'ERROR'}, "No PNG files found")
            return {'CANCELLED'}

        wm = context.window_manager
        wm.progress_begin(0, len(frames))

        try:
            write_apng(frames, output_file, fps)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        finally:
            wm.progress_end()

        self.report({'INFO'}, f"APNG exported: {output_file}")
        return {'FINISHED'}

# ------------------------------------------------------------
# UI Panel
# ------------------------------------------------------------

class APNG_PT_panel(Panel):
    bl_label = "APNG Export"
    bl_idname = "APNG_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "apng_input_dir")
        layout.prop(scene, "apng_output_file")
        layout.prop(scene, "apng_fps")
        layout.operator("render.export_apng", icon="RENDER_ANIMATION")

# ------------------------------------------------------------
# Registration
# ------------------------------------------------------------

def register():
    bpy.utils.register_class(RENDER_OT_export_apng)
    bpy.utils.register_class(APNG_PT_panel)

    bpy.types.Scene.apng_input_dir = StringProperty(
        name="Image Sequence Folder",
        subtype="DIR_PATH"
    )
    bpy.types.Scene.apng_output_file = StringProperty(
        name="Output APNG",
        subtype="FILE_PATH",
        default="//output.apng"
    )
    bpy.types.Scene.apng_fps = IntProperty(
        name="FPS",
        default=24,
        min=1,
        max=120
    )

def unregister():
    bpy.utils.unregister_class(RENDER_OT_export_apng)
    bpy.utils.unregister_class(APNG_PT_panel)

    del bpy.types.Scene.apng_input_dir
    del bpy.types.Scene.apng_output_file
    del bpy.types.Scene.apng_fps

if __name__ == "__main__":
    register()
