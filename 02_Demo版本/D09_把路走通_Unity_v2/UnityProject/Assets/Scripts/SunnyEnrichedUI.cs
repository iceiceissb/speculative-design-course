using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static partial class SunnyUI
{
    static Dictionary<string,Texture2D> previews=new Dictionary<string,Texture2D>();
    static SunnyWorld previewWorld;
    static Camera previewCamera;
    static Texture2D recordImage;
    static string recordImagePath;
    static int selectedRecord=-1;

    public static bool StorePhoto(string path)
    {if(!photo)return false;File.WriteAllBytes(path,photo.EncodeToPNG());return true;}

    static Texture2D ItemPreview(string name)
    {
        Texture2D result;if(previews.TryGetValue(name,out result)&&result)return result;
        if(previewWorld==null)
        {
            previewWorld=new SunnyWorld();previewWorld.root=new GameObject("ItemPreviewRig").transform;previewWorld.root.position=new Vector3(0,-200,0);
            previewCamera=new GameObject("ItemPreviewCamera").AddComponent<Camera>();previewCamera.enabled=false;
            previewCamera.clearFlags=CameraClearFlags.SolidColor;previewCamera.backgroundColor=new Color(1,1,1,0);
            previewCamera.cullingMask=1<<31;previewCamera.orthographic=true;previewCamera.nearClipPlane=.01f;previewCamera.farClipPlane=30;previewCamera.allowHDR=false;
            if(Camera.main)Camera.main.cullingMask&=~(1<<31);
        }
        var item=previewWorld.Asset(name,Vector3.zero);
        foreach(var t in item.GetComponentsInChildren<Transform>())t.gameObject.layer=31;
        var bounds=new Bounds();bool first=true;
        foreach(var r in item.GetComponentsInChildren<Renderer>())
        {if(first){bounds=r.bounds;first=false;}else bounds.Encapsulate(r.bounds);}
        float size=Mathf.Max(bounds.size.x,Mathf.Max(bounds.size.y,bounds.size.z));
        previewCamera.transform.position=bounds.center+new Vector3(1.25f,.9f,-2.1f)*Mathf.Max(size,.4f);
        previewCamera.transform.LookAt(bounds.center);previewCamera.orthographicSize=size*.73f;
        var previous=RenderTexture.active;var rt=RenderTexture.GetTemporary(256,256,24,RenderTextureFormat.ARGB32);
        previewCamera.targetTexture=rt;previewCamera.Render();RenderTexture.active=rt;
        result=new Texture2D(256,256,TextureFormat.RGBA32,false);result.ReadPixels(new Rect(0,0,256,256),0,0);result.Apply();
        previewCamera.targetTexture=null;RenderTexture.active=previous;RenderTexture.ReleaseTemporary(rt);
        item.SetActive(false);Object.Destroy(item);previews[name]=result;return result;
    }

    static void LibraryTask(SunnyGame g)
    {
        Backdrop();Panel(new Rect(300,128,1000,650),Cream);
        Text(343,162,850,48,"换一本书，换一种心情",34,Ink,true);
        Text(343,226,850,40,"预约单：《植物图鉴》   ·   先还书，再找到预约的那本。",21,Muted);
        int stage=!g.basket[0]?0:!g.basket[1]?1:2;
        Pill(343,282,230,"第 "+(stage+1)+" 步 / 3",SunnyWorld.Hex("DFE9F1"));
        if(stage==0)
        {
            GUI.DrawTexture(new Rect(370,340,245,230),ItemPreview("Book"),ScaleMode.ScaleToFit);
            Text(666,355,560,55,"这本已经读完了。",29,Ink,true);
            Text(666,427,560,85,"把它放入还书箱，\n让下一位读者接着读。",23,Muted);
            if(Button(666,537,545,62,"放入还书箱  1"))g.Pick(0);
        }
        else if(stage==1)
        {
            for(int i=0;i<3;i++)
            {
                float x=343+i*303;
                Panel(new Rect(x,340,286,250),SunnyWorld.Hex(i==1?"E7EEDB":"F0EBDD"));
                GUI.DrawTexture(new Rect(x+50,347,185,157),ItemPreview("Book"),ScaleMode.ScaleToFit);
                Text(x+12,510,262,37,g.BookChoices[i],23,Ink,true,TextAnchor.MiddleCenter);
                if(GUI.Button(new Rect(x,340,286,250),GUIContent.none,GUIStyle.none))g.SelectLibraryBook(i);
            }
            Text(343,641,895,38,"点击书名，或按 2 领取预约书。",19,Muted);
        }
        else
        {
            GUI.DrawTexture(new Rect(366,340,245,230),ItemPreview("Book"),ScaleMode.ScaleToFit);
            Text(665,355,560,53,"《植物图鉴》找到了。",29,Ink,true);
            Text(665,429,560,88,"窗边有新开的花，书里也有。\n借好以后，带它一起回家。",23,Muted);
            if(Button(665,537,545,62,"确认借阅，准备回家  3")){g.Pick(2);g.FinishShopping();}
        }
        if(Button(1155,165,100,39,"返回",false))g.panel="";
        Text(343,713,870,31,g.taskFeedback!=""?g.taskFeedback:"1 还书    2 取预约书    3 确认借阅    Enter 完成",17,g.taskFeedback!=""?Coral:Muted);
    }

    static void GardenTask(SunnyGame g)
    {
        Backdrop();Panel(new Rect(350,140,900,615),Cream);
        Text(393,172,800,47,"给今天种下一点绿",34,Ink,true);
        Text(393,235,800,40,"薄荷苗已经备好，种下后记得浇一点水。",21,Muted);
        string[] models={"Seedling","Seedling","WateringCan"};
        string[] notes={"拿好这一株小苗","放进花坛的空位","给根部浇一点水"};
        for(int i=0;i<3;i++)
        {
            float x=393+i*277;bool enabled=i==0||g.basket[i-1];
            Panel(new Rect(x,304,258,252),SunnyWorld.Hex(g.basket[i]?"DCECCF":enabled?"F1EBD7":"EDEDE1"));
            GUI.DrawTexture(new Rect(x+38,309,184,145),ItemPreview(models[i]),ScaleMode.ScaleToFit);
            Text(x+10,455,238,38,g.config.items[i],23,Ink,true,TextAnchor.MiddleCenter);
            Text(x+10,505,238,29,g.basket[i]?"已完成":notes[i],16,Muted,false,TextAnchor.MiddleCenter);
            if(enabled&&GUI.Button(new Rect(x,304,258,252),GUIContent.none,GUIStyle.none))g.Pick(i);
        }
        bool ready=g.basket[0]&&g.basket[1]&&g.basket[2];
        if(Button(393,610,812,66,ready?"种好了，回家的路也该看看啦  →":"按 1 / 2 / 3，依次完成种植",true,ready))g.FinishShopping();
        if(Button(1096,174,109,39,"返回",false))g.panel="";
        if(g.taskFeedback!="")Text(393,704,812,31,g.taskFeedback,18,Coral);
    }

    static void Story(SunnyGame g)
    {
        Backdrop();Panel(new Rect(345,140,910,620),Cream);
        Text(390,175,810,50,g.StoryTitle(),32,Ink,true);
        GUI.DrawTexture(new Rect(385,281,220,270),ItemPreview(g.storyIndex==0?"NoticeBoard":"Walker"),ScaleMode.ScaleToFit);
        Text(648,277,556,340,g.StoryText(),23,Ink);
        if(Button(390,649,810,62,"继续出发  E"))g.CloseStory();
    }

    static void Journal(SunnyGame g)
    {
        Backdrop();Panel(new Rect(85,75,1430,745),Cream);
        Text(125,105,920,57,"一路走来，留下的改变",35,Ink,true);
        Text(125,174,1040,36,"现场照片、地点与处理结果，都保存在这台电脑上。",20,Muted);
        if(Button(1340,112,129,44,"关闭  J",false))g.panel=g.phase==2?"home":"";
        var records=g.save.records;
        if(records.Count==0)
        {
            GUI.DrawTexture(new Rect(230,260,300,310),ItemPreview("NoticeBoard"),ScaleMode.ScaleToFit);
            Text(635,325,700,130,"先留下一条反馈吧。\n\n去程记录的问题，回家时再看看它的变化。",28,Muted);
            return;
        }
        int pages=(records.Count+5)/6;g.journalPage=Mathf.Clamp(g.journalPage,0,pages-1);
        for(int row=0;row<6;row++)
        {
            int i=records.Count-1-g.journalPage*6-row;if(i<0)break;
            var e=records[i];float y=238+row*70;
            Panel(new Rect(125,y,760,60),i==selectedRecord?SunnyWorld.Hex("DDEDD5"):SunnyWorld.Hex("F0ECDC"));
            Text(144,y+6,500,28,e.title,21,Ink,true);
            Text(144,y+34,520,23,g.DistrictName(e.district)+"  ·  第 "+e.day+" 次出行",14,Muted);
            Text(686,y+12,177,33,e.repaired?"已修复":"已接收",18,e.repaired?Teal:Coral,true,TextAnchor.MiddleRight);
            if(GUI.Button(new Rect(125,y,760,60),GUIContent.none,GUIStyle.none))selectedRecord=i;
        }
        if(selectedRecord<0||selectedRecord>=records.Count)selectedRecord=records.Count-1;
        var selected=records[selectedRecord];
        Text(936,242,510,50,selected.title,25,Ink,true);
        string path=string.IsNullOrEmpty(selected.image)?"":Path.Combine(g.ReportDirectory,selected.image);
        if(path!=recordImagePath)
        {
            if(recordImage)Object.Destroy(recordImage);recordImage=null;recordImagePath=path;
            if(path!=""&&File.Exists(path)){recordImage=new Texture2D(2,2);recordImage.LoadImage(File.ReadAllBytes(path));}
        }
        if(recordImage)GUI.DrawTexture(new Rect(936,320,510,287),recordImage,ScaleMode.ScaleToFit);
        else Text(936,357,510,90,"该地点保留了文字记录。",21,Muted);
        Text(936,645,510,70,selected.repaired?"城市服务已处理。\n下次经过时，可以直接走走看。":"城市服务已接收。\n办完今天的事，再沿路看看。",21,Muted);
        if(Button(125,711,150,43,"上一页",false,g.journalPage>0))g.journalPage--;
        Text(300,714,330,36,(g.journalPage+1)+" / "+pages+"   ·   共 "+records.Count+" 条反馈",18,Muted);
        if(Button(650,711,235,43,"下一页",false,g.journalPage<pages-1))g.journalPage++;
    }
}
