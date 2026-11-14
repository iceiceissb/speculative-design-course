using System;
using System.Collections.Generic;
using UnityEngine;

public sealed partial class SunnyWorld
{
    public SunnyDistrict config;
    public Transform noticeBoard,bookCart,gardenPlant;
    public List<Transform> birds=new List<Transform>();
    public List<Vector3> birdBases=new List<Vector3>();

    void BuildDistrictLayout(int district,int repaired)
    {
        config=SunnyDistrict.Make(district);var d=config;
        root=new GameObject("SunnyDistrict_"+district).transform;
        var rand=new System.Random(521+district*17);
        Box("Meadow",new Vector3(48,-.49f,14),new Vector3(160,.35f,90),d.ground);
        Box("Promenade",new Vector3(50,-.16f,0),new Vector3(160,.32f,7.2f),d.paving,true);
        Box("CycleLane",new Vector3(50,-.21f,-5.3f),new Vector3(160,.16f,2.8f),d.theme==1?"91C5CC":"7DCAC5");
        Box("SidewalkEdge",new Vector3(50,-.03f,-3.55f),new Vector3(160,.16f,.20f),"FFF7E2");
        for(int x=-10;x<110;x+=2)
        {
            Box("PavingJoint",new Vector3(x,.006f,0),new Vector3(.018f,.012f,6.8f),"D8CEB8");
            if(x%4==0)Box("CycleDash",new Vector3(x,-.12f,-5.3f),new Vector3(1.4f,.014f,.07f),"FFF7E2");
        }
        for(int lane=-1;lane<=1;lane++)Box("LongPavingJoint",new Vector3(50,.009f,lane*1.65f),new Vector3(140,.008f,.014f),"D8CEB8");
        Asset("Home",new Vector3(3,0,6.1f));
        Asset(d.AssetName,new Vector3(d.destination,0,6.4f));
        if(d.theme==0)Asset("Postbox",new Vector3(11,0,3.05f));
        if(d.theme==1)
        {
            bookCart=Asset("BookCart",new Vector3(d.destination-5,0,3.4f)).transform;
            for(int i=0;i<3;i++)Asset("Bench",new Vector3(38+i*18,0,3.15f));
        }
        if(d.theme==2)
        {
            gardenPlant=Asset("Seedling",new Vector3(d.destination-2.4f,.82f,6.8f),.8f).transform;
            gardenPlant.localScale=Vector3.one*.15f;
            Asset("WateringCan",new Vector3(d.destination+2.1f,.8f,5.2f),.85f);
        }
        foreach(int x in new[]{16,37,60,81})
        {
            var h=Asset(d.theme==1&&x==60?"Library":"Home",new Vector3(x,0,d.theme==2?10.8f:8),d.theme==1&&x==60?.66f:.92f+(x%3)*.045f);
            Recolor(h,"F2ADA0",d.theme==0?(x%2==0?"F4BF7C":"F2ADA0"):d.theme==1?"A9CDD4":"B8D8A5");
        }
        if(d.theme==2)
        {
            for(int i=0;i<9;i++)Asset("Bush",new Vector3(27+i*7,0,4.7f),1.3f);
            for(int i=0;i<6;i++)Asset("Tree",new Vector3(12+i*15,0,7.5f),1.1f);
            for(int i=0;i<20;i++)
            {
                float x=11+i*4.3f;
                if(x<d.destination-4.3f)Box("GardenFencePost",new Vector3(x,.5f,4.45f),new Vector3(.09f,1,.12f),"FFF3DA");
            }
            float fenceEnd=d.destination-4.3f;
            for(int z=0;z<2;z++)Box("GardenFenceRail",new Vector3((8+fenceEnd)*.5f,.35f+z*.35f,4.45f),new Vector3(fenceEnd-8,.08f,.10f),"FFF3DA");
        }
        for(int i=0;i<16;i++)
        {
            float x=-14+i*9,height=4+(float)rand.NextDouble()*6;
            float depth=24+i%3*6;string c=i%3==0?"BDD9CE":i%3==1?"C8DBD5":"CFDFC5";
            Box("DistantTown",new Vector3(x,height/2-.3f,depth),new Vector3(5.7f,height,4),c);
            Box("Roofline",new Vector3(x,height-.2f,depth),new Vector3(5.95f,.22f,4.2f),"DFE8DC");
            for(int floor=1;floor<height/1.7f;floor++)
                for(int window=0;window<3;window++)
                    Box("DistantWindow",new Vector3(x-1.7f+window*1.65f,floor*1.6f,depth-2.02f),new Vector3(.82f,.60f,.025f),"E5ECDF");
        }
        for(int i=0;i<12;i++)
        {
            float x=-4+i*9;
            if(d.theme!=2||i%2==0)Asset("Tree",new Vector3(x,0,5.15f+(i%2)*3),.88f+(i%3)*.10f);
            if(i%2==0)Asset("Lamp",new Vector3(x+2,0,3.35f));
            if(i%3==0)Asset("Bench",new Vector3(x+3.5f,0,3.2f));
            if(i%2==1)Asset("Planter",new Vector3(x+4,0,3.2f),.9f);
        }
        for(int i=0;i<23;i++)
        {
            float x=-7+i*5;
            Asset("Bush",new Vector3(x,-.22f,-8.8f-(i%3)*.7f),1.0f+(i%4)*.2f);
        }
        noticeBoard=Asset("NoticeBoard",new Vector3(d.positions[0]+11,0,3.2f),.9f).transform;
        for(int i=0;i<4;i++)
        {
            Vector3 p=new Vector3(16+i*22,2.6f+i%2,6.6f);
            birds.Add(Asset("Bird",p,.78f).transform);birdBases.Add(p);
        }
        for(int i=0;i<3;i++)
        {
            broken[i]=new GameObject("Before_"+i);broken[i].transform.SetParent(root,false);
            fixedParts[i]=new GameObject("After_"+i);fixedParts[i].transform.SetParent(root,false);
            BuildIssue(i,d.types[i],d.positions[i]);SetRepaired(i,(repaired&(1<<i))!=0);
            for(int j=0;j<6;j++)Box("DetourPaving",new Vector3(d.positions[i]-2.5f+j,.012f,-2.35f),new Vector3(.7f,.018f,.52f),"D8E5B9");
        }
    }

    public void Recolor(GameObject o,string from,string to)
    {
        foreach(var r in o.GetComponentsInChildren<Renderer>())
        {
            var a=r.sharedMaterials;bool changed=false;
            for(int i=0;i<a.Length;i++)if(a[i]==Mat(from)){a[i]=Mat(to);changed=true;}
            if(changed)r.sharedMaterials=a;
        }
    }

    void InvisibleBox(string name,Vector3 p,Vector3 s,Transform parent)
    {var box=Box(name,p,s,"BD8053",true,parent);box.GetComponent<Renderer>().enabled=false;}

    void BuildIssue(int slot,int type,float x)
    {
        var before=broken[slot].transform;var after=fixedParts[slot].transform;
        if(type==0)
        {
            for(int i=0;i<6;i++)
            {
                var p=new Vector3(x+(i%2)*.85f-.4f,0,-.85f+i/2*.85f);
                Asset("Crate",p,1,0,before);InvisibleBox("CargoCollision",p+Vector3.up*.42f,new Vector3(.95f,.84f,.82f),before);
            }
        }
        if(type==1)
        {
            Box("RaisedPaving",new Vector3(x,.17f,0),new Vector3(3.2f,.34f,2.9f),"E4CFAC",true);
            Ramp("WestRamp",x-6,x-1.6f,0,.34f,after);Ramp("EastRamp",x+1.6f,x+6,.34f,0,after);
            Box("StepStripe",new Vector3(x-1.63f,.34f,0),new Vector3(.08f,.015f,2.9f),"FFC94D",false,before);
        }
        if(type==2)
        {
            for(int side=-1;side<=1;side+=2)
            {
                Asset("Bollard",new Vector3(x,0,side*.42f),1,0,before);
                var col=broken[slot].AddComponent<CapsuleCollider>();col.radius=.26f;col.height=1.2f;col.center=new Vector3(x,.6f,side*.42f);
                Asset("Bollard",new Vector3(x,0,side*1.95f),1,0,after);
                var fixedCol=fixedParts[slot].AddComponent<CapsuleCollider>();fixedCol.radius=.24f;fixedCol.height=1.2f;fixedCol.center=new Vector3(x,.6f,side*1.95f);
            }
        }
        if(type==3)
        {
            for(int i=0;i<8;i++)
            {
                float z=-1.1f+i%4*.73f;float xx=x-.48f+i/4*.82f;
                var slab=Box("LiftedPaver",new Vector3(xx,.18f,z),new Vector3(.78f,.36f,.67f),i%2==0?"C8BDA6":"D4C6AC",true,before);
                // The individual slabs stay level for clear physical blocking; cracks are visible between them.
            }
            Box("RepairedPaving",new Vector3(x,.018f,0),new Vector3(2.2f,.036f,3.0f),"E9E4D3",false,after);
        }
        if(type==4)
        {
            for(int i=0;i<3;i++)
            {
                var p=new Vector3(x+(i%2)*.25f,0,(i-1)*.8f);
                Asset("Scooter",p,1,i%2==0?9:-9,before);InvisibleBox("ParkedVehicleCollision",p+Vector3.up*.55f,new Vector3(1.6f,1.1f,.68f),before);
                Asset("Scooter",new Vector3(x+2+i*.9f,0,3.12f),.85f,90,after);
            }
            for(int i=0;i<3;i++)Box("ParkingBay",new Vector3(x+2+i*.9f,.018f,3.14f),new Vector3(.75f,.016f,.06f),"FFF3DA",false,after);
        }
        if(type==5)
        {
            Box("HighPlatform",new Vector3(x,.25f,0),new Vector3(3.2f,.5f,2.9f),"E4CFAC",true);
            Ramp("SteepWest",x-2.25f,x-1.6f,0,.5f,before);Ramp("SteepEast",x+1.6f,x+2.25f,.5f,0,before);
            Ramp("GentleWest",x-7.8f,x-1.6f,0,.5f,after);Ramp("GentleEast",x+1.6f,x+7.8f,.5f,0,after);
        }
        if(type!=1&&type!=5)Box("RestoredLane",new Vector3(x,.012f,0),new Vector3(2.8f,.018f,2.9f),"BEDFC7",false,after);
    }
}
