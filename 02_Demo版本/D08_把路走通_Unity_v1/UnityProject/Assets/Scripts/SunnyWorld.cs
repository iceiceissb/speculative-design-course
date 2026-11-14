using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class SunnyWorld
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
        {"Pink","F2ADA0"},{"Glass","9DDDE1"},{"Tire","303E4A"},{"Orange","FF9F38"}
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
                    var key=r.sharedMaterials[i]?r.sharedMaterials[i].name.Replace("MAT-","").Replace(" (Instance)",""):"Cream";
                    string hex; if(!Palette.TryGetValue(key,out hex))hex="FFF3DA";
                    mapped[i]=Mat(hex);
                }
                r.sharedMaterials=mapped;
            }
            if(name!="Hero")Combine(template);
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
        root=new GameObject("SunnyDistrict_"+district).transform;
        var rand=new System.Random(521+district*17);
        Box("Meadow",new Vector3(48,-.49f,14),new Vector3(160,.35f,90),"B9DA8B");
        Box("Promenade",new Vector3(50,-.16f,0),new Vector3(160,.32f,7.2f),"F3DFC1",true);
        Box("CycleLane",new Vector3(50,-.21f,-5.3f),new Vector3(160,.16f,2.8f),"7DCAC5");
        Box("SidewalkEdge",new Vector3(50,-.03f,-3.55f),new Vector3(160,.16f,.20f),"FFF7E2");
        for(int x=-6;x<110;x+=4)
        {
            Box("PavingJoint",new Vector3(x,.006f,0),new Vector3(.025f,.012f,6.8f),"D8C8A9");
            Box("CycleDash",new Vector3(x,-.12f,-5.3f),new Vector3(1.4f,.014f,.07f),"FFF7E2");
        }
        Asset("Home",new Vector3(3,0,6.1f));
        Asset("Market",new Vector3(97,0,6.4f));
        var houses=new[]{15,33,55,79};
        foreach(var x in houses)
        {
            var h=Asset("Home",new Vector3(x,0,7.2f),1+(float)rand.NextDouble()*.23f);
            foreach(var r in h.GetComponentsInChildren<Renderer>())
                if(r.sharedMaterial==Mat("F2ADA0"))r.sharedMaterial=Mat((district+x)%3==0?"E5C56B":(district+x)%3==1?"A9D7D6":"F3B197");
        }
        for(int i=0;i<20;i++)
        {
            float x=-15+i*7;
            var color=i%3==0?"B3D5CA":i%3==1?"C2DCD5":"CFDFC5";
            float height=4+(float)rand.NextDouble()*8;
            Box("DistantTown",new Vector3(x,height/2-.3f,21+i%3*7),new Vector3(5+(float)rand.NextDouble()*3,height,4),color);
            Box("Roofline",new Vector3(x,height-.2f,21+i%3*7),new Vector3(5.4f,.25f,4.1f),"DAE5D5");
            for(int floor=1;floor<height/2;floor++)
                Box("DistantWindows",new Vector3(x,floor*1.6f,18.97f+i%3*7),new Vector3(3.7f,.50f,.035f),"D6E6D8");
        }
        for(int i=0;i<13;i++)
        {
            float x=-4+i*9;
            Asset("Tree",new Vector3(x,0,5.1f+(i%2)*3),.9f+(i%3)*.12f);
            if(i%2==0)Asset("Lamp",new Vector3(x+2,0,3.35f));
            if(i%3==0)Asset("Bench",new Vector3(x+3,0,3.2f));
            if(i%2==1)Asset("Planter",new Vector3(x+3,0,-3.2f));
        }
        for(int i=0;i<24;i++)
        {
            float x=-7+i*5;
            Asset("Planter",new Vector3(x,-.28f,-8.8f-(i%3)*.7f),.8f+(i%4)*.1f);
        }
        // Raised platform: both the original step and the later ramps have real colliders.
        Box("RaisedPaving",new Vector3(48,.21f,0),new Vector3(3.6f,.42f,2.9f),"E9D2AD",true);
        for(int i=0;i<3;i++)
        {
            broken[i]=new GameObject("Before_"+i);broken[i].transform.SetParent(root,false);
            fixedParts[i]=new GameObject("After_"+i);fixedParts[i].transform.SetParent(root,false);
        }
        for(int i=0;i<6;i++)
        {
            var p=new Vector3(22+(i%2)*.85f-.4f,0,-.85f+i/2*.85f);
            Asset("Crate",p,1,0,broken[0].transform);
            var c=Box("CrateCollision",p+Vector3.up*.42f,new Vector3(.95f,.84f,.82f),"BD8053",true,broken[0].transform);
            c.GetComponent<Renderer>().enabled=false;
        }
        Box("ClearLane",new Vector3(22,.015f,0),new Vector3(3.2f,.015f,2.9f),"A6D9BC",false,fixedParts[0].transform);
        Ramp("WestRamp",44,46.2f,0,.42f,fixedParts[1].transform);
        Ramp("EastRamp",49.8f,52,.42f,0,fixedParts[1].transform);
        Box("StepStripe",new Vector3(46.18f,.42f,0),new Vector3(.08f,.016f,2.9f),"FFBD50",false,broken[1].transform);
        for(int side=-1;side<=1;side+=2)
        {
            Asset("Bollard",new Vector3(72,0,side*.42f),1,0,broken[2].transform);
            var col=broken[2].AddComponent<SphereCollider>();col.radius=.26f;col.center=new Vector3(72,.55f,side*.42f);
            Asset("Bollard",new Vector3(72,0,side*1.95f),1,0,fixedParts[2].transform);
            var after=fixedParts[2].AddComponent<CapsuleCollider>();after.radius=.24f;after.height=1.2f;after.center=new Vector3(72,.6f,side*1.95f);
        }
        for(int i=0;i<3;i++)SetRepaired(i,(repaired&(1<<i))!=0);
        // A clear visual cue for the bypass lane at each interruption.
        foreach(float x in new[]{22f,48f,72f})
            for(int j=0;j<5;j++)Box("DetourPaving",new Vector3(x-2+j, .012f,-2.35f),new Vector3(.7f,.018f,.52f),"D5E4B1");
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
