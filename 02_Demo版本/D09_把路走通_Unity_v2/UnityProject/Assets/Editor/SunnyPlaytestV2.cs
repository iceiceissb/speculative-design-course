using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static class SunnyPlaytestV2
{
    [Serializable] public class Result{public bool passed;public List<string> checks=new List<string>();public List<string> failures=new List<string>();public float seconds;public int themes,obstacleTypes;}
    public static Result result;
    static string output;
    static void Check(bool ok,string name){result.checks.Add(name);if(!ok){result.failures.Add(name);Debug.LogError("SUNNY_V2_FAIL "+name);}else Debug.Log("SUNNY_V2_OK "+name);}
    static IEnumerator Travel(SunnyGame g,float x,float z,float seconds=18)
    {
        float end=Time.realtimeSinceStartup+seconds;g.testDriving=true;
        while(Time.realtimeSinceStartup<end)
        {
            var p=g.player.position;var delta=new Vector2(x-p.x,z-p.z);
            if(delta.magnitude<.18f)break;
            g.testInput=delta.normalized*Mathf.Clamp01(delta.magnitude*2);yield return null;
        }
        g.testInput=Vector2.zero;yield return new WaitForSeconds(.32f);
        Check(Vector2.Distance(new Vector2(g.player.position.x,g.player.position.z),new Vector2(x,z))<.6f,"theme "+g.config.theme+" reach "+x+","+z);
    }
    static IEnumerator Photo(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(Path.Combine(output,name+".png"));yield return new WaitForSeconds(.35f);}

    public static IEnumerator Run(SunnyGame g)
    {
        result=new Result();output=Path.GetFullPath(Path.Combine(Application.dataPath,"../../QA"));Directory.CreateDirectory(output);
        var old=PlayerPrefs.GetString(SunnyGame.SaveKey,"");float start=Time.realtimeSinceStartup;
        g.testReportDirectory=Path.Combine(output,"Reports");g.save=new SunnySave();
        var types=new HashSet<int>();
        foreach(int index in new[]{12,13,11})
        {
            g.BuildDistrict(index);g.Begin();yield return new WaitForSeconds(.6f);
            Check(g.visual.GetComponentsInChildren<Renderer>().Length==6,"hero uses six detailed mesh groups");
            Check(g.config.theme==index%3,"district has own theme");
            for(int slot=0;slot<3;slot++)
            {
                float x=g.config.positions[slot];int type=g.config.types[slot];types.Add(type);
                yield return Travel(g,x-5.2f,0);
                g.Interact();Check(g.panel=="report","issue "+type+" opens correct report");
                if(slot==0)yield return Photo("theme"+g.config.theme+"_report");
                g.SubmitReport();int count=g.save.records.Count;g.SubmitReport();
                Check(g.save.records.Count==count,"duplicate report stays one record");
                var entry=g.save.records[count-1];Check(entry.title==g.config.Issue(slot)&&File.Exists(Path.Combine(g.ReportDirectory,entry.image)),"issue "+type+" saves actual photo and location");
                g.testInput=Vector2.right;yield return new WaitForSeconds(2.1f);g.testInput=Vector2.zero;
                Check(g.player.position.x<x-0.3f,"issue "+type+" physically blocks direct passage");
                yield return Travel(g,g.player.position.x,-2.35f);
                yield return Travel(g,x+8.5f,-2.35f);yield return Travel(g,x+9.5f,0);
                if(slot==0)
                {
                    yield return Travel(g,x+11,0);g.Interact();Check(g.panel=="story","neighborhood notice opens");g.CloseStory();
                    Check((g.save.seenStory[index]&1)!=0,"neighborhood reading is remembered");
                }
            }
            yield return Travel(g,g.config.destination-2,0);g.Interact();Check(g.panel=="shop","destination opens for theme "+g.config.theme);
            if(g.config.theme==1)
            {
                g.Pick(1);Check(!g.basket[1],"library requires returning old book first");g.Pick(0);g.SelectLibraryBook(0);
                Check(!g.basket[1],"wrong library title does not silently finish task");g.SelectLibraryBook(1);g.Pick(2);
            }
            else if(g.config.theme==2)
            {
                g.Pick(2);Check(!g.basket[2],"garden requires planting before watering");g.Pick(0);g.Pick(1);g.Pick(2);
                Check(g.world.gardenPlant.localScale.x>.9f,"plant grows visibly after task");
            }
            else{g.Pick(0);g.Pick(1);g.Pick(2);}
            yield return Photo("theme"+g.config.theme+"_task");g.FinishShopping();yield return new WaitForSeconds(3.7f);
            Check(g.phase==1&&g.save.repaired[index]==7&&g.save.pending[index]==0,"theme "+g.config.theme+" repairs after life task");
            for(int slot=2;slot>=0;slot--)
            {
                yield return Travel(g,g.config.positions[slot]+9,0);
                yield return Travel(g,g.config.positions[slot]-9,0);
                Check(g.player.position.y<.16f,"issue "+g.config.types[slot]+" repaired route descends cleanly");
                if(slot==1)yield return Photo("theme"+g.config.theme+"_return");
            }
            yield return Travel(g,4,0);g.Interact();Check(g.phase==2&&g.panel=="home","theme "+g.config.theme+" returns home");
            var data=JsonUtility.FromJson<SunnySave>(PlayerPrefs.GetString(SunnyGame.SaveKey));
            Check(data.repaired[index]==7&&data.visits[index]==1,"theme "+g.config.theme+" persists progress");
            g.panel="journal";yield return Photo("theme"+g.config.theme+"_journal");
            result.themes++;
        }
        Check(types.Count==6,"all six obstacle types exercised");result.obstacleTypes=types.Count;
        Check(g.save.records.Count==9,"three journeys retain nine distinct records");
        Check(g.save.repaired[12]==7&&g.save.repaired[13]==7&&g.save.repaired[11]==7,"progress survives switching all three themes");
        g.panel="map";g.selectedDistrict=12;yield return Photo("world_v2");
        result.passed=result.failures.Count==0;result.seconds=Time.realtimeSinceStartup-start;
        File.WriteAllText(Path.Combine(output,"playtest_v2_result.json"),JsonUtility.ToJson(result,true));
        if(old==""){PlayerPrefs.DeleteKey(SunnyGame.SaveKey);g.save=new SunnySave();}else{PlayerPrefs.SetString(SunnyGame.SaveKey,old);g.save=JsonUtility.FromJson<SunnySave>(old);}
        PlayerPrefs.Save();g.testReportDirectory=null;g.testDriving=false;g.testInput=Vector2.zero;g.BuildDistrict(g.save.district);g.panel="title";
        Debug.Log("SUNNY_V2_DONE "+result.passed);
    }
}
