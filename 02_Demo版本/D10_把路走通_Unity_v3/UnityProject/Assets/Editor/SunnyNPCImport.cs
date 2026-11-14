using UnityEditor;
using UnityEngine;

public sealed class SunnyNPCImport : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        if(!assetPath.StartsWith("Assets/Resources/NPCs/"))return;
        var i=(ModelImporter)assetImporter;i.importAnimation=true;i.animationType=ModelImporterAnimationType.Legacy;
        i.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;i.isReadable=true;
        i.importNormals=ModelImporterNormals.Calculate;i.normalSmoothingAngle=60;
        var clips=i.defaultClipAnimations;
        foreach(var clip in clips)clip.loopTime=true;
        i.clipAnimations=clips;
    }
}
