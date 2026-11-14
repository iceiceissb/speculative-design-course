using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static class SunnyFirstPersonCheck
{
    [Serializable] public class Result { public bool passed;public List<string> checks=new List<string>(),failures=new List<string>();public float seconds; }
    public static Result result;
    static string output;
    static void Check(bool value,string name){result.checks.Add(name);if(!value){result.failures.Add(name);Debug.LogError("SUNNY_FP_FAIL "+name);}}
    static IEnumerator Travel(SunnyGame g,float x,float z,float timeout=26)
    {
        float end=Time.realtimeSinceStartup+timeout;g.testDriving=true;
        while(Time.realtimeSinceStartup<end)
        {
            Vector2 d=new Vector2(x-g.player.position.x,z-g.player.position.z);if(d.magnitude<.18f)break;
            float heading=-Mathf.Atan2(d.y,d.x)*Mathf.Rad2Deg;
            float error=Mathf.DeltaAngle(g.chairYaw,heading);
            float turn=Mathf.Clamp(error/24,-1,1);
            float forward=Mathf.Clamp01((d.magnitude-.10f)*1.5f)*Mathf.Clamp01(1-Mathf.Abs(error)/55);
            g.testInput=new Vector2(turn,forward);yield return null;
        }
        g.testInput=Vector2.zero;yield return new WaitForSeconds(.25f);
        Check(Vector2.Distance(new Vector2(g.player.position.x,g.player.position.z),new Vector2(x,z))<.65f,"FP drives to "+x+","+z);
    }
    static IEnumerator Photo(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(Path.Combine(output,name+".png"));yield return new WaitForSeconds(.3f);}
    public static IEnumerator Run(SunnyGame g)
    {
        result=new Result();output=Path.GetFullPath(Application.dataPath+"/../../QA");float start=Time.realtimeSinceStartup;
        string old=PlayerPrefs.GetString(SunnyGame.SaveKey,"");g.save=new SunnySave();g.testReportDirectory=Path.Combine(output,"ReportsFP");
        g.SetFirstPerson(false);g.BuildDistrict(12);g.Begin();yield return new WaitForSeconds(.7f);
        foreach(var skin in UnityEngine.Object.FindObjectsOfType<SkinnedMeshRenderer>())
        {
            var baked=new Mesh();skin.BakeMesh(baked);var bounds=new Bounds();bool first=true;
            foreach(var v in baked.vertices){var p=skin.transform.TransformPoint(v);if(first){bounds=new Bounds(p,Vector3.zero);first=false;}else bounds.Encapsulate(p);}
            Check(bounds.size.y>1.4f&&bounds.size.y<2.1f,"deformed NPC has actual human size: "+skin.transform.parent.name);
            Check(bounds.min.y>-.12f&&bounds.min.y<.20f,"NPC feet are at ground level");UnityEngine.Object.Destroy(baked);
        }
        g.SetFirstPerson(true);yield return new WaitForSeconds(.8f);
        for(int slot=0;slot<3;slot++)
        {
            float x=g.config.positions[slot];yield return Travel(g,x-5.2f,0);
            g.Interact();Check(g.panel=="report","first-person opens report "+slot);
            if(slot==0)yield return Photo("fp_full_report");
            g.SubmitReport();Check((g.save.pending[12]&(1<<slot))!=0,"first-person submits issue "+slot);
            yield return Travel(g,x-5.2f,-2.35f);yield return Travel(g,x+8.5f,-2.35f);yield return Travel(g,x+9.5f,0);
        }
        yield return Travel(g,g.config.destination-2,0);g.Interact();Check(g.panel=="shop","first-person arrives at market");
        g.Pick(0);g.Pick(1);g.Pick(2);yield return Photo("fp_full_task");g.FinishShopping();yield return new WaitForSeconds(3.5f);
        Check(g.save.repaired[12]==7&&g.phase==1,"first-person life task repairs submitted issues");
        for(int slot=2;slot>=0;slot--)
        {
            yield return Travel(g,g.config.positions[slot]+8,0);yield return Travel(g,g.config.positions[slot]-8,0);
            Check(g.player.position.y<.15f,"first-person drives repaired route "+slot);
            if(slot==1)yield return Photo("fp_full_return");
        }
        yield return Travel(g,4,0);g.Interact();Check(g.phase==2&&g.panel=="home","complete first-person journey returns home");
        Check(g.save.records.Count==3&&g.save.records.TrueForAll(r=>r.repaired),"first-person retains three repaired photo records");
        yield return Photo("fp_full_home");
        result.passed=result.failures.Count==0;result.seconds=Time.realtimeSinceStartup-start;
        File.WriteAllText(Path.Combine(output,"first_person_result.json"),JsonUtility.ToJson(result,true));
        if(old==""){PlayerPrefs.DeleteKey(SunnyGame.SaveKey);g.save=new SunnySave();}else{PlayerPrefs.SetString(SunnyGame.SaveKey,old);g.save=JsonUtility.FromJson<SunnySave>(old);}
        PlayerPrefs.Save();g.testReportDirectory=null;g.testDriving=false;g.testInput=Vector2.zero;g.SetFirstPerson(false);g.BuildDistrict(g.save.district);g.panel="title";
        Debug.Log("SUNNY_FP_DONE "+result.passed);
    }
}
