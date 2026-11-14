using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class SunnyBuild
{
    public const string ScenePath="Assets/Scenes/SunnyPath.unity";
    [MenuItem("Sunny Path/Prepare Scene")]
    public static void Setup()
    {
        Directory.CreateDirectory("Assets/Scenes");
        PlayerSettings.companyName="SunnyPathStudio";PlayerSettings.productName="把路走通";
        PlayerSettings.defaultScreenWidth=1600;PlayerSettings.defaultScreenHeight=900;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;PlayerSettings.resizableWindow=true;
        PlayerSettings.runInBackground=true;PlayerSettings.colorSpace=ColorSpace.Linear;
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Standalone,ScriptingImplementation.Mono2x);
        QualitySettings.SetQualityLevel(3,true);
        string materialPath="Assets/Resources/SunnyStandard.mat";
        if(!AssetDatabase.LoadAssetAtPath<Material>(materialPath))
            AssetDatabase.CreateAsset(new Material(Shader.Find("Standard")),materialPath);
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("SunnyPathGame").AddComponent<SunnyGame>();
        EditorSceneManager.SaveScene(scene,ScenePath);
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(ScenePath,true)};
        AssetDatabase.SaveAssets();Debug.Log("SUNNY_SCENE_READY");
    }

    [MenuItem("Sunny Path/Build Windows")]
    public static void BuildWindows()
    {
        string parent=Path.GetFullPath(Path.Combine(Application.dataPath,"../.."));
        string output=Path.Combine(parent,"Build","SunnyPath.exe");
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{ScenePath},locationPathName=output,target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
        File.WriteAllText(Path.Combine(parent,"QA","build_result.json"),JsonUtility.ToJson(new BuildResultData{result=result.summary.result.ToString(),bytes=(long)result.summary.totalSize,errors=result.summary.totalErrors,warnings=result.summary.totalWarnings,path=output},true));
        Debug.Log("SUNNY_BUILD_"+result.summary.result);
    }
    [Serializable] public class BuildResultData{public string result,path;public long bytes;public int errors,warnings;}
}

public sealed class SunnyModelImport : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        if(!assetPath.StartsWith("Assets/Resources/Models/"))return;
        var importer=(ModelImporter)assetImporter;
        importer.importAnimation=false;importer.globalScale=1;
        importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
        importer.isReadable=true;
    }
}
