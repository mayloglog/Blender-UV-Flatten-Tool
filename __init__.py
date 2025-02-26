bl_info = {
    "name": "UV Flatten Tool",
    "author": "maylog",
    "version": (1, 1),
    "blender": (4, 4, 0),
    "location": "Object > UV Flatten",
    "description": "Flatten mesh to active UV coordinates and store as shape key",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector

class MeshUVFlatten:
    def __init__(self, obj):
        self.obj = obj
    
    def mark_seams_by_uv_islands(self, bm):
        """使用低级别API按UV孤岛标记缝合边"""
        if not self.obj.data.uv_layers:
            raise ValueError("Object needs a UV map")
        
        uv_layer = bm.loops.layers.uv.active
        seams = set()
        
        # 遍历所有边，检查UV坐标差异以标记缝合边
        for edge in bm.edges:
            if len(edge.link_loops) < 2:  # 跳过边界边或单面边
                continue
            uv_coords = [loop[uv_layer].uv.copy() for loop in edge.link_loops]
            for i in range(1, len(uv_coords)):
                if (uv_coords[0] - uv_coords[i]).length > 0.0001:  # UV差异阈值
                    edge.seam = True
                    seams.add(edge)
                    break
        
        print(f"Marked {len(seams)} edges as seams")
        if not seams:
            print("Warning: No seams were marked. Ensure UV map has distinct islands.")
        return bm
    
    def split_by_uv_islands(self, bm):
        """仅切开标记为缝合边的边"""
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
        mesh = self.obj.data
        
        # 获取当前活动UV贴图名称
        if not mesh.uv_layers.active:
            raise ValueError("No active UV layer found")
        active_uv_name = mesh.uv_layers.active.name
        shape_key_name = f"{active_uv_name}_Flattened"
        
        # 创建BMesh并标记、分割缝合边
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bm = self.mark_seams_by_uv_islands(bm)
        bm = self.split_by_uv_islands(bm)
        
        # 将分割后的网格应用到对象
        bm.to_mesh(mesh)
        mesh.update()
        
        # 检查是否存在基础形态键（考虑None情况）
        if not mesh.shape_keys or len(mesh.shape_keys.key_blocks) == 0:  # 无形态键时创建Basis
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
    bl_label = "UV Flatten"
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
    """将操作符添加到Object菜单"""
    self.layout.operator(MESH_OT_uv_flatten.bl_idname, text="UV Flatten")

def register():
    bpy.utils.register_class(MESH_OT_uv_flatten)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # 添加到Object菜单

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_flatten)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()