This plugin allows you to slap the model flat by UV and store it as a morph key. This operation generates stitching edges along the UV silos and splits the model by stitching edges for quick triangulation to quadrilateralization or further processing of the model.
Note: This operation will make changes to the original model and add a Morphological Key, if there is a special need to back up the original model file.
The principle of the plug-in is to first generate the stitching edge by UV silo, then cut the model by the stitching edge, then transform the XYZ values of the model by UV coordinates, and finally store the deformation into the morphology key with the name of the current UV layer.


本插件可以按UV拍平模型，并存储为形态键。 此操作会沿UV孤岛生成缝合边，并按缝合边拆开模型， 以便快捷三角面转四边面，或者进一步处理模型。
注意：此操作会让更改原始模型并增加形态键，如果有特殊需要，需要备份原始模型文件。
插件原理是首先按UV孤岛生成缝合边，然后按缝合边切开模型，然后按UV坐标变换模型的XYZ值，最后把形变存储至以当前UV层为名称的形态键中。
