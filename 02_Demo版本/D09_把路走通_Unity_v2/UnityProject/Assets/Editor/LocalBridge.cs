using UnityEditor;
using MCPForUnity.Editor;

[InitializeOnLoad]
public static class LocalBridge
{
    static LocalBridge()
    {
        EditorApplication.delayCall += () => {
            if (!EditorApplication.isCompiling) McpCiBoot.StartStdioForCi();
        };
    }
}
