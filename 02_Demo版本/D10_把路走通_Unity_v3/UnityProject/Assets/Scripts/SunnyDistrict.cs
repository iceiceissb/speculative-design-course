using UnityEngine;

public sealed class SunnyDistrict
{
    public int index,theme;
    public float destination;
    public float[] positions;
    public int[] types;
    public string destinationName,taskTitle,taskNote;
    public string[] items;
    public string sky,ground,paving;
    public static readonly string[] IssueNames={"通道被货箱占用","人行道缺少坡道","阻车柱间距过窄","地砖翘起破损","车辆占用通道","入口坡道过陡"};
    public static readonly string[] IssueFacts={
        "货箱挡住了沿街通路。请清理占用，保留连续的通行空间。",
        "人行道中段抬高，入口缺少平缓衔接。请核查高差并补充坡道。",
        "柱口空间不足，轮椅无法直接通过。请核查并调整柱位。",
        "几块地砖翘起，路面存在明显高差。请修复破损并找平。",
        "停放的车辆挡住了通路。请清理占用，并调整停放位置。",
        "入口已有坡面，但过陡，轮椅需要绕行。请重新核查并调整坡面。"
    };
    public static SunnyDistrict Make(int index)
    {
        var d=new SunnyDistrict();d.index=index;d.theme=index%3;
        if(d.theme==0)
        {
            d.destination=97;d.positions=new[]{22f,48f,72f};d.types=new[]{0,1,2};
            d.destinationName="晴日市集";d.taskTitle="去市集买菜";d.taskNote="按购物清单选三样新鲜食材，买好后回家做饭。";
            d.items=new[]{"番茄","胡萝卜","橙子"};d.sky="B0E4ED";d.ground="BDDFA2";d.paving="F4E3C3";
        }
        else if(d.theme==1)
        {
            d.destination=94;d.positions=new[]{25f,50f,73f};d.types=new[]{3,2,1};
            d.destinationName="梧桐图书馆";d.taskTitle="去图书馆换本书";d.taskNote="归还读完的书，再找出预约的《植物图鉴》。";
            d.items=new[]{"归还旧书","植物图鉴","确认借阅"};d.sky="BDE2EB";d.ground="B9D8B4";d.paving="E9E4D3";
        }
        else
        {
            d.destination=92;d.positions=new[]{20f,45f,69f};d.types=new[]{4,5,0};
            d.destinationName="邻里共享花园";d.taskTitle="去共享花园种薄荷";d.taskNote="领一株薄荷苗，种进花坛，再给它浇点水。";
            d.items=new[]{"领取薄荷苗","种进花坛","浇水完成"};d.sky="B6E8DE";d.ground="ACD894";d.paving="F3E1BC";
        }
        return d;
    }
    public string Issue(int slot){return IssueNames[types[slot]];}
    public string Fact(int slot){return IssueFacts[types[slot]];}
    public string AssetName{get{return theme==0?"Market":theme==1?"Library":"Pavilion";}}
}
