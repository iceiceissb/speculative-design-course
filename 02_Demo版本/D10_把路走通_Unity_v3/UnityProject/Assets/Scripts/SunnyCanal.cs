using System.Collections.Generic;
using UnityEngine;

public sealed partial class SunnyWorld
{
    public float bridgeX;
    readonly List<Rect> walkable=new List<Rect>();
    static Font streetFont;
    public Vector3 ConstrainPosition(Vector3 p)
    {
        Vector2 q=new Vector2(p.x,p.z);
        foreach(var r in walkable)if(r.Contains(q))return p;
        float best=float.MaxValue;Vector2 closest=q;
        foreach(var r in walkable)
        {
            var c=new Vector2(Mathf.Clamp(q.x,r.xMin,r.xMax),Mathf.Clamp(q.y,r.yMin,r.yMax));
            float d=(c-q).sqrMagnitude;if(d<best){best=d;closest=c;}
        }
        p.x=closest.x;p.z=closest.y;return p;
    }

    public GameObject StreetText(string name,string text,Vector3 p,float size,Transform parent=null,float yaw=0,string color="23465C")
    {
        if(!streetFont)streetFont=Font.CreateDynamicFontFromOSFont(new[]{"Microsoft YaHei","SimHei","Arial"},40);
        var o=new GameObject(name);o.transform.SetParent(parent?parent:root,false);o.transform.localPosition=p;o.transform.localRotation=Quaternion.Euler(0,yaw,0);
        var t=o.AddComponent<TextMesh>();t.font=streetFont;t.fontSize=60;t.characterSize=size*.20f;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.text=text;t.color=Hex(color);
        o.GetComponent<MeshRenderer>().sharedMaterial=streetFont.material;return o;
    }

    void BuildCanalDistrict()
    {
        var d=config;bridgeX=d.theme==0?58:d.theme==1?62:54;
        walkable.Clear();walkable.Add(new Rect(0,-2.75f,d.destination+4,5.45f));
        walkable.Add(new Rect(31,2.3f,11,4.4f));
        walkable.Add(new Rect(d.destination-5.5f,2.3f,10.5f,1.8f));
        walkable.Add(new Rect(bridgeX-1.05f,-13.4f,2.1f,11.3f));
        walkable.Add(new Rect(bridgeX-9,-15.1f,18,2.4f));
        var scenic=new GameObject("CanalArchitecture").transform;scenic.SetParent(root,false);
        Box("DryRiverMargin",new Vector3(49,-.16f,-4.05f),new Vector3(160,.32f,.9f),"EBDCC0",true,scenic);
        Box("CanalWater",new Vector3(49,-.64f,-8.6f),new Vector3(170,.045f,8.2f),"69CBCB",false,scenic).GetComponent<Renderer>().sharedMaterial=WaterMaterial();
        foreach(float z in new[]{-4.65f,-12.8f})
        {
            Box("LimestoneEmbankment",new Vector3(49,-.50f,z),new Vector3(160,.95f,.4f),"D1CBB5",true,scenic);
            Box("BankCoping",new Vector3(49,-.045f,z),new Vector3(160,.16f,.56f),"FFF0D4",true,scenic);
            for(int x=-20;x<130;x+=3)
                Box("BankStoneJoint",new Vector3(x,-.49f,z< -8?z+.211f:z-.211f),new Vector3(.022f,.70f,.012f),"AEBBAE",false,scenic);
        }
        Box("OppositeBank",new Vector3(49,-.18f,-15.1f),new Vector3(160,.36f,4.3f),"DCE4C6",true,scenic);
        Box("OppositeMeadow",new Vector3(49,-.49f,-26),new Vector3(160,.35f,23),"BBD9A2",false,scenic);
        Box("BridgeDeck",new Vector3(bridgeX,-.10f,-8.65f),new Vector3(4.1f,.20f,9.65f),"F5E6CA",true,scenic);
        for(int i=0;i<25;i++)Box("BridgeDeckJoint",new Vector3(bridgeX,.006f,-13.25f+i*.385f),new Vector3(4,.009f,.02f),"D4C5AB",false,scenic);
        foreach(float side in new[]{-1f,1f})
        {
            float x=bridgeX+side*1.91f;
            for(int i=0;i<9;i++)Box("BridgePost",new Vector3(x,.49f,-12.9f+i*1.05f),new Vector3(.10f,1.02f,.10f),"229A9C",true,scenic);
            foreach(float h in new[]{.36f,.91f})Box("BridgeRail",new Vector3(x,h,-8.65f),new Vector3(.07f,.075f,9.1f),"229A9C",true,scenic);
            Box("BridgeKerb",new Vector3(x,.08f,-8.65f),new Vector3(.16f,.16f,9.5f),"FFF3DA",true,scenic);
        }
        for(int x=-16;x<128;x+=4)
        {
            if(Mathf.Abs(x-bridgeX)<3)continue;
            foreach(float z in new[]{-4.88f,-12.6f})
            {
                Box("RiverSafetyPost",new Vector3(x,.40f,z),new Vector3(.075f,.8f,.075f),"559D9E",false,scenic);
                Box("RiverSafetyRail",new Vector3(x+1.96f,.73f,z),new Vector3(3.98f,.055f,.055f),"559D9E",false,scenic);
            }
        }
        for(int i=0;i<12;i++)
        {
            float x=-6+i*10;
            Asset("Bush",new Vector3(x,-.03f,-16.8f),1.0f+(i%2)*.2f);
            if(i%3==0)Asset("Tree",new Vector3(x+2,0,-19),1.05f);
        }
        Asset("Bench",new Vector3(bridgeX-5.0f,0,-14.2f),1,180);
        Asset("Planter",new Vector3(bridgeX+6,0,-14.1f),.75f);
        // A real paved pocket square, with furniture outside the continuous wheelchair route.
        Box("PocketSquare",new Vector3(36.5f,-.075f,4.95f),new Vector3(13,.15f,6.0f),d.theme==1?"E6E4D4":"F0DFC0",true,scenic);
        for(int i=0;i<11;i++)Box("SquareJoint",new Vector3(31.5f+i,.008f,5.1f),new Vector3(.012f,.012f,5.4f),"D5CCB6",false,scenic);
        Asset("Bench",new Vector3(34,0,7.05f));Asset("Bench",new Vector3(40,0,7.05f));
        Asset("Tree",new Vector3(31,0,8.1f),1.15f);Asset("Tree",new Vector3(43,0,8.1f),1.15f);
        Box("DestinationForecourt",new Vector3(d.destination,-.075f,3.0f),new Vector3(13,.15f,4.1f),d.theme==1?"DFE6DC":"F2DAB4",true,scenic);
        foreach(int x in new[]{8,29,65,85})
        {
            Box("WayfindingPole",new Vector3(x,1.05f,3.42f),new Vector3(.07f,2.1f,.07f),"229A9C",false,scenic);
            Box("WayfindingPanel",new Vector3(x,1.78f,3.36f),new Vector3(2.2f,.52f,.11f),"FFF3DA",false,scenic);
            StreetText("RouteSign",d.destinationName+"  →",new Vector3(x,1.79f,3.28f),.13f);
        }
        Box("BridgeNamePole",new Vector3(bridgeX-2.55f,.75f,-3.75f),new Vector3(.07f,1.5f,.07f),"559D9E",false,scenic);
        Box("BridgeNamePanel",new Vector3(bridgeX-2.55f,1.45f,-3.75f),new Vector3(1.2f,.4f,.1f),"FFF3DA",false,scenic);
        StreetText("BridgePlaque","晴溪桥",new Vector3(bridgeX-2.55f,1.45f,-3.82f),.17f);
        if(d.theme==0)
        {
            for(int i=0;i<3;i++)
            {
                float x=65+i*7;
                Box("MarketStallCounter",new Vector3(x,.52f,4.7f),new Vector3(2.1f,1.04f,.8f),i%2==0?"EDB28E":"87C8BA",false,scenic);
                Box("StallCanopy",new Vector3(x,2.3f,4.8f),new Vector3(2.5f,.12f,1.8f),i%2==0?"FFC94D":"F57857",false,scenic);
                foreach(float side in new[]{-1f,1f})Box("CanopyPost",new Vector3(x+side*1.05f,1.18f,5.3f),new Vector3(.06f,2.36f,.06f),"BD8053",false,scenic);
                for(int j=0;j<4;j++)Asset(j%2==0?"Orange":"Tomato",new Vector3(x-.6f+j*.4f,1.05f,4.5f),.6f);
            }
            StreetText("SquareTitle","晴溪小集 · 今日新鲜",new Vector3(36.5f,2.15f,7.6f),.19f);
        }
        else if(d.theme==1)
        {
            Asset("BookCart",new Vector3(32,0,5.65f),1,90);
            StreetText("SquareTitle","梧桐树下 · 街角阅读",new Vector3(36.5f,2.15f,7.6f),.19f);
            for(int i=0;i<3;i++)Asset("Book",new Vector3(33.4f+i*.3f,.61f,7.0f),.45f,20*i);
        }
        else
        {
            for(int i=0;i<5;i++)
            {
                float x=28+i*13;
                Box("CommunityGardenBed",new Vector3(x,.38f,6),new Vector3(2.6f,.76f,1.4f),"BD8053",false,scenic);
                Box("GardenSoil",new Vector3(x,.77f,6),new Vector3(2.4f,.04f,1.2f),"665145",false,scenic);
                for(int j=0;j<3;j++)Asset("Seedling",new Vector3(x-.75f+j*.7f,.78f,6),.65f);
            }
            StreetText("SquareTitle","邻里花圃 · 一起生长",new Vector3(36.5f,2.15f,7.6f),.19f);
        }
        Combine(scenic.gameObject);
    }

    Material WaterMaterial()
    {
        const string key="CanalWater";Material m;if(materials.TryGetValue(key,out m))return m;
        var source=Resources.Load<Material>("SunnyWater");
        m=source?new Material(source):new Material(Shader.Find("Standard"));m.name="Sunny_CanalWater";m.color=Hex("65C6CC");materials[key]=m;return m;
    }
}
