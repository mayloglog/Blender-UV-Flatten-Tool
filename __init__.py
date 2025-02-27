bl_info = {
    "name": "UV Flatten Tool",
    "author": "maylog",
    "version": (1, 0, 2),
    "blender": (4, 4, 0),
    "location": "Object > Flatten UV to SK",
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
        """使用官方命令沿UV孤岛生成缝合边"""
        if not self.obj.data.uv_layers:
            raise ValueError("Object needs a UV map")
        
        # 切换到编辑模式并选择所有面
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # 设置UV编辑器上下文
        original_area = bpy.context.area.type
        bpy.context.area.type = 'IMAGE_EDITOR'
        bpy.context.space_data.mode = 'UV'
        
        # 选择所有UV面并生成缝合边
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.seams_from_islands()
        
        # 恢复上下文并返回物体模式
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
        seams = set()
        for edge in bm.edges:
            if edge.seam:
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
        mesh = self.obj.data
        
        if not mesh.uv_layers.active:
            raise ValueError("No active UV layer found")
        active_uv_name = mesh.uv_layers.active.name
        shape_key_name = f"{active_uv_name}_Flattened"
        
        # 标记UV孤岛的缝合边
        self.mark_seams_by_uv_islands()
        
        # 创建BMesh并分割缝合边
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bm = self.split_by_uv_islands(bm)
        
        # 将分割后的网格应用到对象
        bm.to_mesh(mesh)
        mesh.update()
        
        # 检查是否存在基础形态键
        if not mesh.shape_keys or len(mesh.shape_keys.key_blocks) == 0:
            basis_key = self.obj.shape_key_add(name="Basis", from_mix=False)
            for i, vert in enumerate(mesh.vertices):
                basis_key.data[i].co = vert.co
        
        # 检查是否已存在同名形态键，避免重复
        if not mesh.shape_keys.key_blocks.get(shape_key_name):
            bm = self.flatten_to_uv(bm, active_uv_name)
            shape_key = self.obj.shape_key_add(name=shape_key_name, from_mix=False)
            for i, vert in enumerate(bm.verts):
                shape_key.data[i].co = vert.co
        
        bm.free()

class MESH_OT_uv_flatten(bpy.types.Operator):
    bl_idname = "mesh.uv_flatten"
    bl_label = "Flatten UV to SK"  # 内部标签保持简洁
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

def menu_func(self, context):
    self.layout.operator(MESH_OT_uv_flatten.bl_idname, text="Flatten UV to SK")

def register():
    bpy.utils.register_class(MESH_OT_uv_flatten)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_flatten)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()