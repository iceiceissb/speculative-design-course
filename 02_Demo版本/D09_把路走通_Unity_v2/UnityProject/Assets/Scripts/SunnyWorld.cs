using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

public sealed partial class SunnyWorld
{
    public Transform root;
    public GameObject[] broken = new GameObject[3];
    public GameObject[] fixedParts = new GameObject[3];
    public List<Transform> flowers = new List<Transform>();
    readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
    readonly Dictionary<string, GameObject> templates = new Dictionary<string, GameObject>();
    readonly List<Mesh> runtimeMeshes = new List<Mesh>();
    public static Color Hex(string h) { Color c; ColorUtility.TryParseHtmlString("#"+h,out c); return c; }
    static readonly Dictionary<string,string> Palette = new Dictionary<string,string> {
        {"Cream","FFF3DA"},{"Coral","F57857"},{"Teal","20A9AA"},{"Ink","23465C"},
        {"Yellow","FFC94D"},{"LeafLight","A5D86F"},{"Leaf","62BC65"},{"Skin","DFA578"},
        {"Hair","343B4A"},{"Denim","375B91"},{"White","FFFDF1"},{"Wood","BD8053"},
        {"Pink","F2ADA0"},{"Glass","9DDDE1"},{"Tire","303E4A"},{"Orange","FF9F38"},
        {"Steel","94B0B7"},{"RoofDark","CE624C"},{"Paper","FAF5DC"},{"Cobalt","4C7BBA"},
        {"Lilac","B6A4D5"},{"DarkWood","94664B"},{"Soil","665145"}
    };

    public Material Mat(string hex)
    {
        Material m;
        if(materials.TryGetValue(hex,out m))return m;
        var baseMaterial=Resources.Load<Material>("SunnyStandard");
        m=baseMaterial?new Material(baseMaterial):new Material(Shader.Find("Standard"));m.name="Sunny_"+hex;
        m.color=Hex(hex);
        m.SetFloat("_Glossiness",.12f);materials[hex]=m;return m;
    }

    public GameObject Box(string name,Vector3 p,Vector3 size,string color,bool solid=false,Transform parent=null)
    {
        var o=GameObject.CreatePrimitive(PrimitiveType.Cube);o.name=name;
        o.transform.SetParent(parent?parent:root,false);o.transform.localPosition=p;o.transform.localScale=size;
        o.GetComponent<Renderer>().sharedMaterial=Mat(color);
        if(!solid)UnityEngine.Object.Destroy(o.GetComponent<Collider>());
        return o;
    }

    public GameObject Asset(string name,Vector3 pos,float scale=1,float yaw=0,Transform parent=null)
    {
        GameObject template;
        if(!templates.TryGetValue(name,out template))
        {
            var source=Resources.Load<GameObject>("Models/"+name);
            if(!source)throw new InvalidOperationException("Required Blender asset missing: "+name);
            template=UnityEngine.Object.Instantiate(source);
            template.name="Template_"+name;template.transform.position=Vector3.zero;
            foreach(var r in template.GetComponentsInChildren<Renderer>())
            {
                var mapped=new Material[r.sharedMaterials.Length];
                for(int i=0;i<mapped.Length;i++)
                {
                    var key=r.sharedMaterials[i]?r.sharedMaterials[i].name.Replace("MAT-V2_","").Replace("MAT-","").Replace(" (Instance)",""):"Cream";
                    key=System.Text.RegularExpressions.Regex.Replace(key,@"\.\d+$","");
                    string hex; if(!Palette.TryGetValue(key,out hex))hex="FFF3DA";
                    mapped[i]=Mat(hex);
                }
                r.sharedMaterials=mapped;
            }
            if(name!="Hero"&&name!="Walker")Combine(template);
            template.SetActive(false);
            templates[name]=template;
        }
        var o=new GameObject(name);o.transform.SetParent(parent?parent:root,false);
        o.transform.localPosition=pos;o.transform.localRotation=Quaternion.Euler(0,yaw,0);o.transform.localScale=Vector3.one*scale;
        var model=UnityEngine.Object.Instantiate(template,o.transform,false);
        model.name=name+"Model";model.SetActive(true);model.transform.localPosition=Vector3.zero;
        // Keep the FBX up-axis conversion and import scale; turn its forward direction into the game convention.
        model.transform.localRotation=Quaternion.Euler(0,180,0)*model.transform.localRotation;
        return o;
    }

    void Combine(GameObject o)
    {
        var groups=new Dictionary<Material,List<CombineInstance>>();
        var old=o.GetComponentsInChildren<MeshFilter>();
        foreach(var mf in old)
        {
            var renderer=mf.GetComponent<MeshRenderer>();
            if(!renderer||!mf.sharedMesh)continue;
            for(int s=0;s<mf.sharedMesh.subMeshCount;s++)
            {
                var mat=renderer.sharedMaterials[Mathf.Min(s,renderer.sharedMaterials.Length-1)];
                if(!groups.ContainsKey(mat))groups[mat]=new List<CombineInstance>();
                groups[mat].Add(new CombineInstance{mesh=mf.sharedMesh,subMeshIndex=s,transform=o.transform.worldToLocalMatrix*mf.transform.localToWorldMatrix});
            }
        }
        foreach(var entry in groups)
        {
            var child=new GameObject("Merged_"+entry.Key.name);child.transform.SetParent(o.transform,false);
            var mesh=new Mesh();mesh.indexFormat=IndexFormat.UInt32;
            mesh.CombineMeshes(entry.Value.ToArray(),true,true);mesh.RecalculateBounds();runtimeMeshes.Add(mesh);
            child.AddComponent<MeshFilter>().sharedMesh=mesh;child.AddComponent<MeshRenderer>().sharedMaterial=entry.Key;
        }
        foreach(var mf in old){mf.gameObject.SetActive(false);UnityEngine.Object.Destroy(mf.gameObject);}
    }

    public void Build(int district,int repaired)
    {
        BuildDistrictLayout(district,repaired);
    }
    void Ramp(string name,float x1,float x2,float h1,float h2,Transform parent)
    {
        float z=1.45f;
        var v=new[]{new Vector3(x1,0,-z),new Vector3(x1,h1,-z),new Vector3(x2,h2,-z),new Vector3(x2,0,-z),
                    new Vector3(x1,0,z),new Vector3(x1,h1,z),new Vector3(x2,h2,z),new Vector3(x2,0,z)};
        int[] t={0,1,2,0,2,3,4,6,5,4,7,6,1,5,6,1,6,2,0,3,7,0,7,4,0,4,5,0,5,1,3,2,6,3,6,7};
        var mesh=new Mesh();mesh.vertices=v;mesh.triangles=t;mesh.RecalculateNormals();runtimeMeshes.Add(mesh);
        var o=new GameObject(name);o.transform.SetParent(parent,false);
        o.AddComponent<MeshFilter>().sharedMesh=mesh;o.AddComponent<MeshRenderer>().sharedMaterial=Mat("A6D9BC");
        o.AddComponent<MeshCollider>().sharedMesh=mesh;
    }

    public void SetRepaired(int i,bool value){broken[i].SetActive(!value);fixedParts[i].SetActive(value);}
    public void Dispose()
    {
        if(root)UnityEngine.Object.Destroy(root.gameObject);
        foreach(var t in templates.Values)if(t)UnityEngine.Object.Destroy(t);
        foreach(var m in materials.Values)if(m)UnityEngine.Object.Destroy(m);
        foreach(var mesh in runtimeMeshes)if(mesh)UnityEngine.Object.Destroy(mesh);
        templates.Clear();materials.Clear();runtimeMeshes.Clear();
    }
}
