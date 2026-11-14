using System;
using UnityEngine;

public sealed partial class SunnyWorld
{
    public Transform Resident(string asset,Vector3 position,int variation,bool walking)
    {
        var source=Resources.Load<GameObject>("NPCs/"+asset);
        if(!source)throw new InvalidOperationException("Missing licensed character: "+asset);
        var wrapper=new GameObject("Neighbour_"+asset+"_"+variation).transform;wrapper.SetParent(root,false);wrapper.localPosition=position;
        var pivot=new GameObject("NPCVisualPivot").transform;pivot.SetParent(wrapper,false);
        var model=UnityEngine.Object.Instantiate(source,pivot,false);model.name="Quaternius_"+asset;
        var renderers=model.GetComponentsInChildren<Renderer>();
        string[] shirts={"C5ACD8","ECA184","7FBFB8","EBC174","B1CFA2","E4A5A2","95BDC8"};
        foreach(var r in renderers)
        {
            var mapped=r.sharedMaterials;
            for(int i=0;i<mapped.Length;i++)
            {
                string n=mapped[i]?mapped[i].name.ToLowerInvariant():"shirt";
                string hex=n.Contains("skin")?variation%3==0?"E6BD9E":variation%3==1?"EBC9AF":"C89978":
                    n.Contains("hair")?variation==0?"7E838A":"303542":
                    n.Contains("face")||n.Contains("eye")?"303542":
                    n.Contains("shoe")?"F4EDDC":
                    n.Contains("pant")||n.Contains("belt")?"4D7180":shirts[variation%shirts.Length];
                mapped[i]=Mat(hex);
            }
            r.sharedMaterials=mapped;
        }
        var animation=model.GetComponent<Animation>();if(!animation)animation=model.AddComponent<Animation>();
        string chosen=null;
        foreach(var clip in Resources.LoadAll<AnimationClip>("NPCs/"+asset))
        {
            if(clip.name.StartsWith("__"))continue;
            if(animation.GetClip(clip.name)==null)animation.AddClip(clip,clip.name);
            string expected=walking?"Walk":"Idle";
            if(clip.name.Contains(expected)&&!clip.name.Contains("Carry"))chosen=clip.name;
        }
        if(chosen==null)throw new InvalidOperationException("NPC clip missing: "+asset);
        animation.wrapMode=WrapMode.Loop;animation.Play(chosen);animation[chosen].wrapMode=WrapMode.Loop;animation[chosen].speed=walking?.62f:1;animation[chosen].normalizedTime=variation*.17f;
        animation.Sample();
        // Size the deformed geometry itself: imported skin bounds can conceal FBX unit errors.
        var bounds=new Bounds();bool first=true;
        foreach(var r in model.GetComponentsInChildren<SkinnedMeshRenderer>())
        {
            var baked=new Mesh();r.BakeMesh(baked);
            foreach(var v in baked.vertices)
            {
                var p=wrapper.InverseTransformPoint(r.transform.TransformPoint(v));
                if(first){bounds=new Bounds(p,Vector3.zero);first=false;}else bounds.Encapsulate(p);
            }
            r.localBounds=baked.bounds;r.updateWhenOffscreen=true;UnityEngine.Object.Destroy(baked);
        }
        if(first||bounds.size.y<.001f)throw new InvalidOperationException("NPC deformed mesh is empty: "+asset);
        // The FBX vertices, rest bones and animation translations are already in metres.
        // Keep the skeleton at unit scale; apply only the ground offset and facing rotation.
        float scale=1;
        pivot.localScale=Vector3.one*scale;pivot.localRotation=Quaternion.Euler(0,90,0);
        pivot.localPosition=pivot.localRotation*(-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z)*scale);
        return wrapper;
    }
}

public sealed partial class SunnyGame
{
    void SpawnNeighbours()
    {
        for(int i=0;i<7;i++)
        {
            bool walking=i>=3;
            string asset=i==0||i==3?"OldClassy_Female":i%2==0?"Casual_Male":"Casual_Female";
            float x=i==0?config.positions[0]+7:i==1?config.positions[1]+11:i==2?config.destination-10:i==3?13:i==4?38:i==5?67:87;
            float z=i==4?5.4f:i==0?2.28f:2.12f;
            var resident=world.Resident(asset,new Vector3(x,0,z),i,walking);
            resident.rotation=Quaternion.Euler(0,i%2==0?0:180,0);
            residents.Add(resident);residentBases.Add(resident.position);
        }
    }

    void AnimateResidents()
    {
        for(int i=0;i<residents.Count;i++)
        {
            if(!residents[i]||i<3)continue;
            var p=residentBases[i];float span=i==4?2.2f:3.5f;
            float cycle=elapsed*.16f+i*.83f;
            p.x+=Mathf.Sin(cycle)*span;residents[i].position=p;
            residents[i].rotation=Quaternion.Euler(0,Mathf.Cos(cycle)>0?0:180,0);
        }
        for(int i=0;i<world.birds.Count;i++)if(world.birds[i])
        {
            var p=world.birdBases[i];p.x+=Mathf.Sin(elapsed*.32f+i)*4;p.y+=Mathf.Sin(elapsed*1.3f+i)*.25f;
            world.birds[i].position=p;world.birds[i].rotation=Quaternion.Euler(0,Mathf.Cos(elapsed*.32f+i)>0?0:180,Mathf.Sin(elapsed*3+i)*5);
        }
    }
}
