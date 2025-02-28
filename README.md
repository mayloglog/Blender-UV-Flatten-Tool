UV Flatten Tool is a straightforward plugin that flattens a mesh based on active UV coordinates and stores it as a shape key.
While Blender's Geometry Nodes can achieve similar results, this plugin’s shape keys enable convenient follow-up operations like animation or tweaking.

Tutorial:
1. Select a mesh object with a UV map.
2. Go to the “Object” menu and click “Flatten UV to SK.”
3. In the dialog, choose:
   - “Use Existing Seams”: Use pre-marked seams.
   - “Generate Seams”: Let the plugin generate seams (older files may need copying to a new scene).
4. Confirm to flatten the UV and create a shape key.
5. Adjust the shape key value in the “Shape Keys” panel to see the effect.
Note: The plugin modifies the original model; back up your file first.

UV Flatten Tool 是一个简单易用的插件，用于将网格按活动UV坐标压平并存储为形态键。
虽然Blender的几何节点也能实现类似功能，但此插件生成的形态键便于用户进行后续编辑和操作，如动画或调整。
使用教程：
1. 选择一个有UV贴图的网格物体。
2. 在“Object”菜单中点击“Flatten UV to SK”。
3. 在弹出的对话框中选择：
   - “Use Existing Seams”：使用已标记的缝合边。
   - “Generate Seams”：让插件生成缝合边（老文件可能需复制到新场景）。
4. 点击确认，插件将压平UV并生成形态键。
5. 在“Shape Keys”面板调整形态键值以查看效果。
注意：插件会修改原始模型，请备份文件。
