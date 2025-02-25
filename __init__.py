bl_info = {
    "name": "UV Flatten Tool",
    "author": "maylog",
    "version": (2, 0),
    "blender": (4, 4, 0),
    "location": "View3D > Tools > UV Flatten",
    "description": "Flatten mesh to active UV coordinates and store as shape key",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector

class MeshUVFlatten:
    def __init__(self, obj):
        self.obj = obj
    
    def mark_seams_by_uv_islands(self):
        """按UV孤岛生成缝合边"""
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')  # 选择所有面
        
        # 临时切换到UV编辑器
        original_area = bpy.context.area.type
        bpy.context.area.type = 'IMAGE_EDITOR'
        bpy.context.space_data.mode = 'UV'
        
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.seams_from_islands()
        
        bpy.context.area.type = original_area
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 验证缝合边数量
        mesh = self.obj.data
        seam_count = sum(1 for edge in mesh.edges if edge.use_seam)
        print(f"Marked {seam_count} edges as seams")
        if seam_count == 0:
            print("Warning: No seams were marked. Ensure UV map has distinct islands.")
    
    def split_by_uv_islands(self, bm):
        """仅切开标记为缝合边的边"""
        if not self.obj.data.uv_layers:
            raise ValueError("Object needs a UV map")
        
        seams = set()
        for edge in bm.edges:
            if edge.seam:  # 只分割标记为缝合边的边
                seams.add(edge)
        
        if seams:
            bmesh.ops.split_edges(bm, edges=list(seams))
            print(f"Split {len(seams)} seam edges")
        else:
            print("No seam edges detected for splitting")
        
        return bm
    
    def flatten_to_uv(self, bm, uv_layer_name):
        """根据指定UV层计算摊平位置"""
        uv_layer = bm.loops.layers.uv[uv_layer_name]
        for face in bm.faces:
            for loop in face.loops:
                vert = loop.vert
                uv = loop[uv_layer].uv
                vert.co = Vector((uv.x, uv.y, 0.0))
        return bm
    
    def apply_flatten_as_shape_key(self):
        """将摊平结果存储为形态键，使用当前活动UV名称"""
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = self.obj.data
        
        # 获取当前活动UV贴图名称
        if not mesh.uv_layers.active:
            raise ValueError("No active UV layer found")
        active_uv_name = mesh.uv_layers.active.name
        shape_key_name = f"{active_uv_name}_Flattened"
        
        # 先标记UV孤岛的缝合边
        self.mark_seams_by_uv_islands()
        
        # 创建BMesh并分割缝合边
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bm = self.split_by_uv_islands(bm)
        
        # 将分割后的网格应用到对象
        bm.to_mesh(mesh)
        mesh.update()
        
        # 在分割后创建Basis形态键（仅创建一次）
        if not mesh.shape_keys or not mesh.shape_keys.key_blocks.get("Basis"):
            basis_key = self.obj.shape_key_add(name="Basis", from_mix=False)
            for i, vert in enumerate(mesh.vertices):
                basis_key.data[i].co = vert.co
        
        # 检查是否已存在同名形态键，避免重复
        if not mesh.shape_keys.key_blocks.get(shape_key_name):
            # 计算摊平状态并存储为活动UV命名的形态键
            bm = self.flatten_to_uv(bm, active_uv_name)
            shape_key = self.obj.shape_key_add(name=shape_key_name, from_mix=False)
            for i, vert in enumerate(bm.verts):
                shape_key.data[i].co = vert.co
        
        bm.free()

class MESH_OT_uv_flatten(bpy.types.Operator):
    bl_idname = "mesh.uv_flatten"
    bl_label = "Flatten to UV"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH')
    
    def execute(self, context):
        try:
            obj = context.active_object
            flattener = MeshUVFlatten(obj)
            flattener.apply_flatten_as_shape_key()
            active_uv_name = obj.data.uv_layers.active.name
            self.report({'INFO'}, f"UV flatten stored as shape key '{active_uv_name}_Flattened'")
            return {'FINISHED'}
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class VIEW3D_PT_uv_flatten(bpy.types.Panel):
    bl_label = "UV Flatten"
    bl_idname = "VIEW3D_PT_uv_flatten"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.uv_flatten", text="Flatten to UV")
        
        # 添加说明文字并启用自动换行
        layout.label(text="This operation will create a shape key to flatten the UV.", translate=False)
        layout.label(text="Ensure the object has a UV map with seams at the edges.", translate=False)
        layout.label(text="If faces are separated individually, manually merge", translate=False)
        layout.label(text="overlapping vertices by material after flattening.", translate=False)

def register():
    bpy.utils.register_class(MESH_OT_uv_flatten)
    bpy.utils.register_class(VIEW3D_PT_uv_flatten)

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_flatten)
    bpy.utils.unregister_class(VIEW3D_PT_uv_flatten)

if __name__ == "__main__":
    register()