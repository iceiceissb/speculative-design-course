using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static class SunnyPlaytest
{
    [Serializable] public class Result{public bool passed;public List<string> checks=new List<string>();public List<string> failures=new List<string>();public float seconds;}
    static Result result;
    static string output;
    static void Check(bool ok,string name){result.checks.Add(name);if(!ok){result.failures.Add(name);Debug.LogError("SUNNY_QA_FAIL "+name);}else Debug.Log("SUNNY_QA_OK "+name);}
    static IEnumerator Travel(SunnyGame g,float x,float z,float seconds=20)
    {
        float end=Time.realtimeSinceStartup+seconds;
        g.testDriving=true;
        while(Time.realtimeSinceStartup<end)
        {
            var p=g.player.position;var delta=new Vector2(x-p.x,z-p.z);
            if(delta.magnitude<.18f)break;
            g.testInput=delta.normalized*Mathf.Clamp01(delta.magnitude*2);
            yield return null;
        }
        g.testInput=Vector2.zero;
        yield return new WaitForSeconds(.32f);
        Check(Vector2.Distance(new Vector2(g.player.position.x,g.player.position.z),new Vector2(x,z))<.6f,"reach "+x+","+z);
    }
    static IEnumerator Photo(string name)
    {yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(Path.Combine(output,name+".png"));yield return new WaitForSeconds(.5f);}

    public static IEnumerator Run(SunnyGame g)
    {
        result=new Result();output=Path.GetFullPath(Path.Combine(Application.dataPath,"../../QA"));Directory.CreateDirectory(output);
        float start=Time.realtimeSinceStartup;
        string old=PlayerPrefs.GetString(SunnyGame.SaveKey,"");
        g.save=new SunnySave();g.BuildDistrict(12);g.Begin();
        yield return new WaitForSeconds(.8f);
        yield return Travel(g,17.3f,0);
        g.Interact();Check(g.panel=="report","report panel opens near first obstacle");
        yield return Photo("qa_report");g.SubmitReport();Check(g.save.pending[12]==1,"report is pending, geometry not repaired early");
        yield return Photo("qa_before");
        g.testInput=Vector2.right;yield return new WaitForSeconds(2);
        g.testInput=Vector2.zero;Check(g.player.position.x<21.2f,"crates physically block direct travel");
        yield return Travel(g,g.player.position.x,-2.35f);
        yield return Travel(g,27,-2.35f);yield return Travel(g,29,0);
        yield return Travel(g,42.6f,0);g.Interact();g.SubmitReport();
        g.testInput=Vector2.right;yield return new WaitForSeconds(2);
        g.testInput=Vector2.zero;Check(g.player.position.x<46.1f,"raised paving physically blocks direct travel");
        yield return Travel(g,g.player.position.x,-2.35f);yield return Travel(g,54,-2.35f);yield return Travel(g,55,0);
        yield return Travel(g,66.5f,0);g.Interact();g.SubmitReport();
        g.testInput=Vector2.right;yield return new WaitForSeconds(2.1f);
        g.testInput=Vector2.zero;Check(g.player.position.x<72,"narrow bollards physically block direct travel");
        yield return Travel(g,g.player.position.x,-2.35f);yield return Travel(g,76,-2.35f);yield return Travel(g,78,0);
        yield return Travel(g,94,0);g.Interact();Check(g.panel=="shop","market task opens");
        g.Pick(0);g.Pick(1);g.Pick(2);yield return Photo("qa_shopping");g.FinishShopping();
        yield return new WaitForSeconds(4);
        Check(g.phase==1&&g.save.repaired[12]==7&&g.save.pending[12]==0,"shopping resolves reported issues and starts return");
        Check(!g.world.broken[0].activeSelf&&g.world.fixedParts[0].activeSelf,"repaired state swaps visible geometry");
        yield return Travel(g,78,0);yield return Travel(g,54,0);
        yield return Travel(g,41,0); // crosses the actual two-sided ramp, no teleport
        Check(g.player.position.y<.2f,"wheelchair descends repaired ramp back to paving");
        yield return Travel(g,24,0);yield return Photo("qa_after");yield return Travel(g,4,0);
        g.Interact();Check(g.phase==2&&g.panel=="home","return home completes trip");
        var restored=JsonUtility.FromJson<SunnySave>(PlayerPrefs.GetString(SunnyGame.SaveKey));
        Check(restored.repaired[12]==7&&restored.visits[12]==1,"completed repairs survive serialized save");
        Check(g.Available(13)&&!g.Available(0),"completed trip unlocks adjacent districts only");
        g.panel="map";g.selectedDistrict=13;yield return Photo("qa_world_map");
        g.StartSelected();yield return new WaitForSeconds(.5f);
        Check(g.district==13&&g.save.repaired[12]==7&&g.save.repaired[13]==0,"new district keeps previous repairs and supplies new issues");
        result.passed=result.failures.Count==0;result.seconds=Time.realtimeSinceStartup-start;
        File.WriteAllText(Path.Combine(output,"playtest_result.json"),JsonUtility.ToJson(result,true));
        if(old==""){PlayerPrefs.DeleteKey(SunnyGame.SaveKey);g.save=new SunnySave();}else{PlayerPrefs.SetString(SunnyGame.SaveKey,old);g.save=JsonUtility.FromJson<SunnySave>(old);}
        PlayerPrefs.Save();
        g.testDriving=false;g.testInput=Vector2.zero;g.BuildDistrict(g.save.district);g.panel="title";
        Debug.Log("SUNNY_QA_DONE "+result.passed);
    }
}
