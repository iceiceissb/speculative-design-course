using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

[Serializable] public sealed class SunnyRecord
{
    public int district,slot,day;
    public string title,image;
    public bool repaired;
}

public sealed partial class SunnyGame
{
    public SunnyDistrict config;
    public int selectedBook=-1,taskStep,storyIndex=-1,journalPage;
    public float cameraFov=33;
    public string testReportDirectory;
    public string taskFeedback="";
    public void TaskHint(string message){taskFeedback=message;Toast(message,3);}
    public string[] BookChoices={"城市散步记","植物图鉴","远方的岛屿"};
    public string ReportDirectory{get{return string.IsNullOrEmpty(testReportDirectory)?Path.Combine(Application.persistentDataPath,"ReportsV3"):testReportDirectory;}}
    public void PreviewRoute(int theme){BuildDistrict(theme==0?12:theme==1?13:11);panel="title";}
    public int TotalTrips(){int n=0;foreach(int v in save.visits)n+=v;return n;}
    public int NearbyStory()
    {
        if(player==null||config==null)return -1;
        if(Mathf.Abs(player.position.x-(config.positions[0]+11))<2.8f&&Mathf.Abs(player.position.z-world.noticeBoard.position.z)<4.5f)return 0;
        if(residents.Count>1&&Mathf.Abs(player.position.x-residents[1].position.x)<2.8f&&Mathf.Abs(player.position.z-residents[1].position.z)<4.5f)return 1;
        return -1;
    }
    public string StoryTitle()
    {
        if(storyIndex==0)return "街角留言板";
        return config.theme==0?"周姨 · 街坊邻居":config.theme==1?"阿澄 · 阅读爱好者":"小满 · 花园志愿者";
    }
    public string StoryText()
    {
        bool improved=save.repaired[district]!=0;
        if(storyIndex==0)
        {
            if(config.theme==0)return "周末的小市集又要开了。\n\n店家在招呼大家带自己的购物袋，长椅旁会有鲜花和手作摊。\n\n留言角贴着一句话：\n“来逛逛吧，慢慢挑，不着急。”";
            if(config.theme==1)return "图书馆本周推荐：\n《植物图鉴》《城市散步记》\n\n周三下午，有人在窗边读诗。\n活动不收门票，带上想读的书就行。";
            return "共享花园的小约定：\n\n种下以后，在小牌子上留个名字。\n天气热的时候，早晚来浇一点水。\n薄荷长大后，欢迎邻居们来摘两片泡茶。";
        }
        if(config.theme==0)return improved?"“刚才看见门口那几箱货搬走了。\n我也能直接推过去，不用绕大半圈。\n\n今天的橙子挺甜，回家记得尝尝。”":"“今天市集有新到的橙子。\n\n我一般走外侧，货箱常堆在中间。\n你要是顺路，帮大家留一条反馈吧。”";
        if(config.theme==1)return improved?"“这段路铺平以后，我终于可以自己来借书了。\n\n如果找到喜欢的那本，记得告诉我书名。”":"“我预约了一本书，想自己去拿。\n那几块翘起的砖，总让人得绕到另一边。\n\n希望下次来能顺顺当当。”";
        return improved?"“车挪到停放区以后，这儿宽敞多了。\n\n你种的是薄荷吧？我上周种的罗勒也发新叶了。\n过几天再一起看看。”":"“花园的水壶就在木架旁。\n\n入口那段坡有点急，我通常从侧面走。\n今天也带了一株小苗，准备种在窗边。”";
    }
    public void CloseStory()
    {
        if(storyIndex>=0){save.seenStory[district]|=1<<storyIndex;Persist();}
        panel="";
    }
    public void SelectLibraryBook(int choice)
    {
        if(!basket[0]){TaskHint("先把读完的书放进还书箱。");return;}
        if(choice!=1){TaskHint("今天预约的是《植物图鉴》，再找找看。");return;}
        selectedBook=choice;Pick(1);
    }
    public void AddRecord(int slot)
    {
        string filename="district_"+district+"_issue_"+slot+".png";
        Directory.CreateDirectory(ReportDirectory);
        bool captured=SunnyUI.StorePhoto(Path.Combine(ReportDirectory,filename));
        save.records.Add(new SunnyRecord{district=district,slot=slot,day=TotalTrips()+1,title=config.Issue(slot),image=captured?filename:"",repaired=false});
    }
    public void CompleteRecord(int slot)
    {
        foreach(var entry in save.records)if(entry.district==district&&entry.slot==slot)entry.repaired=true;
    }
    Vector3 LimitChairMotion(Vector3 intended)
    {
        if(intended.sqrMagnitude<.0000001f)return intended;
        float length=intended.magnitude,allowed=length;
        var hits=Physics.BoxCastAll(player.position+Vector3.up*.75f,new Vector3(.76f,.57f,.52f),intended/length,visual.rotation,length+.035f,~0,QueryTriggerInteraction.Ignore);
        foreach(var hit in hits)
        {
            if(hit.collider.transform.IsChildOf(player)||hit.normal.y>.90f)continue;
            allowed=Mathf.Min(allowed,Mathf.Max(0,hit.distance-.025f));
        }
        return intended*(allowed/length);
    }
}
