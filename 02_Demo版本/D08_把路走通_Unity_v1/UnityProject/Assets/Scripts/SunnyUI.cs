using UnityEngine;

public static class SunnyUI
{
    static Font font;
    static Texture2D round,white,photo;
    static GUIStyle label,card;
    static readonly Color Ink=SunnyWorld.Hex("23465C"),Teal=SunnyWorld.Hex("178F91"),Muted=SunnyWorld.Hex("68817E"),Coral=SunnyWorld.Hex("EF7857"),Cream=SunnyWorld.Hex("FFF9EC");
    static readonly string[] Titles={"坡道被占用","人行道有台阶","阻车柱间距过窄"};
    static readonly string[] Facts={"货箱占用了沿街通道。轮椅需要从外侧绕行，通道应保持畅通。","人行道中段抬高，入口没有平缓衔接。建议核查并补充坡道。","柱口的通行宽度不足。建议核查柱位，让轮椅能够直接通过。"};
    static readonly float[] Xs={22,48,72};

    static void Init()
    {
        if(font)return;
        font=Font.CreateDynamicFontFromOSFont(new[]{"Microsoft YaHei","SimHei","Arial"},20);
        white=new Texture2D(1,1);white.SetPixel(0,0,Color.white);white.Apply();
        round=new Texture2D(40,40,TextureFormat.RGBA32,false);
        for(int y=0;y<40;y++)for(int x=0;x<40;x++)
        {float dx=Mathf.Max(12-x,Mathf.Max(x-27,0)),dy=Mathf.Max(12-y,Mathf.Max(y-27,0));float a=Mathf.Clamp01(12.5f-Mathf.Sqrt(dx*dx+dy*dy));round.SetPixel(x,y,new Color(1,1,1,a));}
        round.Apply();
        label=new GUIStyle{font=font,wordWrap=true,richText=false};
        card=new GUIStyle();card.normal.background=round;card.border=new RectOffset(14,14,14,14);
    }

    static void Panel(Rect r,Color color)
    {GUI.color=color;GUI.Box(r,GUIContent.none,card);GUI.color=Color.white;}
    static void Rect(Rect r,Color color){GUI.color=color;GUI.DrawTexture(r,white);GUI.color=Color.white;}
    static void Text(float x,float y,float w,float h,string value,int size=20,Color? color=null,bool strong=false,TextAnchor align=TextAnchor.UpperLeft)
    {label.fontSize=size;label.fontStyle=strong?FontStyle.Bold:FontStyle.Normal;label.normal.textColor=color??Ink;label.alignment=align;GUI.Label(new Rect(x,y,w,h),value,label);}
    static bool Button(float x,float y,float w,float h,string value,bool primary=true,bool enabled=true)
    {
        var r=new Rect(x,y,w,h);bool hover=r.Contains(Event.current.mousePosition);
        Color color=!enabled?SunnyWorld.Hex("E1E9DD"):primary?(hover?SunnyWorld.Hex("20A6A5"):Teal):(hover?SunnyWorld.Hex("E4ECDD"):SunnyWorld.Hex("EFF2E6"));
        Panel(r,color);Text(x+12,y+1,w-24,h-2,value,21,!enabled?Muted:primary?Color.white:Ink,true,TextAnchor.MiddleCenter);
        return enabled&&GUI.Button(r,GUIContent.none,GUIStyle.none);
    }
    static void Pill(float x,float y,float w,string value,Color color)
    {Panel(new Rect(x,y,w,34),color);Text(x+12,y+1,w-24,30,value,15,Ink,false,TextAnchor.MiddleCenter);}

    public static void RecordFrame(Camera cam)
    {
        if(photo)Object.Destroy(photo);
        var rt=RenderTexture.GetTemporary(640,360,24);var previous=cam.targetTexture;var active=RenderTexture.active;
        cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;
        photo=new Texture2D(640,360,TextureFormat.RGB24,false);photo.ReadPixels(new Rect(0,0,640,360),0,0);photo.Apply();
        cam.targetTexture=previous;RenderTexture.active=active;RenderTexture.ReleaseTemporary(rt);
    }

    public static void Draw(SunnyGame g)
    {
        Init();float s=Mathf.Min(Screen.width/1600f,Screen.height/900f);
        var old=GUI.matrix;GUI.matrix=Matrix4x4.TRS(new Vector3((Screen.width-1600*s)/2,(Screen.height-900*s)/2,0),Quaternion.identity,new Vector3(s,s,1));
        if(g.panel=="title")Title(g);
        else
        {
            Hud(g);WorldLabels(g);
            if(g.panel=="")Context(g);
            if(g.panel=="report")Report(g);
            if(g.panel=="shop")Shop(g);
            if(g.panel=="home")Home(g);
            if(g.panel=="map")Map(g);
            if(g.panel=="pause")Pause(g);
            if(g.panel==""&&Time.unscaledTime<g.toastUntil)
            {Panel(new Rect(430,146,740,58),new Color(1,.987f,.94f,.96f));Text(452,153,696,44,g.lastMessage,20,Ink,false,TextAnchor.MiddleCenter);}
        }
        GUI.matrix=old;
    }

    static void Title(SunnyGame g)
    {
        Pill(64,49,142,"SUNNY PATH",SunnyWorld.Hex("FFF3DA"));
        Text(64,100,530,63,"把路走通",48,Ink,true);
        Panel(new Rect(64,222,570,508),new Color(1,.985f,.94f,.96f));
        Text(100,255,470,124,"出门走走，\n让路更好走。",43,Ink,true);
        Text(100,410,465,90,"坐上轮椅，去街角买点新鲜的。\n沿路留下反馈，看看回家时的变化。",23,Muted);
        Pill(100,516,170,"今天 · 去市集买菜",SunnyWorld.Hex("FCE7BA"));
        if(Button(100,583,468,66,"开始今天的出行  →"))g.Begin();
        Text(100,667,468,32,"Enter 开始    ·    A / D 沿街移动    ·    W / S 绕行",16,Muted);
        Text(65,824,800,32,"每次出门办一件自己的事，回家的路都会变好一点。",19,Ink);
        Text(1210,51,320,34,"向阳里  /  午后晴天",20,Ink,false,TextAnchor.MiddleRight);
    }

    static void Hud(SunnyGame g)
    {
        Panel(new Rect(32,28,363,120),new Color(1,.986f,.94f,.95f));
        Text(54,40,320,29,g.DistrictName(g.district)+"  /  午后晴天",16,Muted);
        Text(54,77,320,45,g.phase==0?"去市集买菜":g.phase==1?"沿着变好的路回家":"今天，走得更远了一点",25,Ink,true);
        Panel(new Rect(1198,28,369,108),new Color(1,.986f,.94f,.95f));
        Text(1220,39,320,28,"这段街区的通行改善",16,Muted);
        int n=g.Count(g.save.repaired[g.district]);
        for(int i=0;i<3;i++)Panel(new Rect(1220+i*105,83,91,9),i<n?Teal:SunnyWorld.Hex("E6DCC8"));
        Text(1419,36,122,40,n+" / 3",24,Teal,true,TextAnchor.MiddleRight);
        Panel(new Rect(32,827,805,47),new Color(1,.986f,.94f,.91f));
        Text(52,830,765,40,"A / D  沿街走     W / S  绕行     E  互动     M  城市地图     Esc  暂停",17,Ink,false,TextAnchor.MiddleLeft);
        if(Button(1384,827,183,47,"城市地图  M",false)) {g.selectedDistrict=g.district;g.panel="map";}
    }

    static Vector2 Project(SunnyGame g,Vector3 p)
    {var v=g.cam.WorldToScreenPoint(p);float s=Mathf.Min(Screen.width/1600f,Screen.height/900f);return new Vector2((v.x-(Screen.width-1600*s)/2)/s,(Screen.height-v.y-(Screen.height-900*s)/2)/s);}

    static void WorldLabels(SunnyGame g)
    {
        if(g.panel!="")return;
        for(int i=0;i<3;i++)
        {
            if(Mathf.Abs(g.player.position.x-Xs[i])>13)continue;
            bool fixedAlready=(g.save.repaired[g.district]&(1<<i))!=0,pending=(g.save.pending[g.district]&(1<<i))!=0;
            var p=Project(g,new Vector3(Xs[i],2.2f,0));
            Panel(new Rect(p.x-102,p.y,204,37),fixedAlready?SunnyWorld.Hex("C9E9CE"):SunnyWorld.Hex("FFF1CF"));
            Text(p.x-94,p.y+1,188,34,fixedAlready?"已改善 · 可以直行":pending?"已上报 · 待处理":Titles[i],16,Ink,true,TextAnchor.MiddleCenter);
        }
        if(g.player.position.x>85)
        {
            var p=Project(g,new Vector3(97,3.45f,4.5f));
            Panel(new Rect(p.x-119,p.y,238,51),SunnyWorld.Hex("FFF6DB"));Text(p.x-110,p.y,220,50,"晴 日 市 集",26,Teal,true,TextAnchor.MiddleCenter);
        }
        if(g.player.position.x<13)
        {
            var p=Project(g,new Vector3(3,3.45f,4.3f));Pill(p.x-72,p.y,144,"我的家",SunnyWorld.Hex("FFF1CF"));
        }
    }

    static void Context(SunnyGame g)
    {
        string hint="";
        if(g.phase==1&&g.player.position.x<6)hint="E   回到家，把今天的变化留在地图上";
        else if(g.phase==0&&g.player.position.x>91)hint="E   进入市集，挑选今天的食材";
        else for(int i=0;i<3;i++)if(Mathf.Abs(g.player.position.x-Xs[i])<5.8f)
        {
            if((g.save.repaired[g.district]&(1<<i))!=0)hint="道路已经改善，可以直接通过";
            else if((g.save.pending[g.district]&(1<<i))!=0)hint="已留下反馈 · W / S 可以从外侧绕行";
            else hint="E   记录这里的通行问题     ·     W / S 绕行";
        }
        if(hint!="") {Panel(new Rect(440,738,720,59),new Color(1,.986f,.94f,.96f));Text(458,744,684,47,hint,21,Ink,true,TextAnchor.MiddleCenter);}
    }

    static void Backdrop(){Rect(new Rect(0,0,1600,900),new Color(.93f,.96f,.91f,.66f));}

    static void Report(SunnyGame g)
    {
        Backdrop();Panel(new Rect(360,135,880,625),Cream);
        Text(399,165,770,43,"留下一条通行反馈",31,Ink,true);
        Pill(399,224,200,"已定位 · "+g.DistrictName(g.district),SunnyWorld.Hex("E1ECDD"));
        if(photo)GUI.DrawTexture(new Rect(399,286,420,237),photo,ScaleMode.ScaleToFit);
        Text(849,285,330,75,Titles[g.reportIndex],27,Ink,true);
        Text(849,374,330,132,Facts[g.reportIndex],21,Muted);
        Text(399,549,780,61,"智能轮椅已整理现场图片与位置。确认后交给城市服务处理，\n你可以继续完成今天的行程。",20,Muted);
        if(Button(399,651,537,61,"确认上报  E / Enter"))g.SubmitReport();
        if(Button(957,651,242,61,"先不提交",false))g.panel="";
    }

    static void Shop(SunnyGame g)
    {
        Backdrop();Panel(new Rect(350,140,900,615),Cream);
        Text(393,172,800,47,"今天，想吃点新鲜的",34,Ink,true);
        Text(393,235,800,40,"点选三样食材，买好以后就沿路回家。",21,Muted);
        string[] items={"番茄","胡萝卜","橙子"};string[] colors={"F57857","FFC94D","FFAA4B"};
        for(int i=0;i<3;i++)
        {
            float x=393+i*277;
            Panel(new Rect(x,304,258,235),SunnyWorld.Hex(g.basket[i]?"DEEDD6":"F1ECD9"));
            Panel(new Rect(x+83,329,91,90),SunnyWorld.Hex(colors[i]));
            Text(x+14,436,230,35,items[i],25,Ink,true,TextAnchor.MiddleCenter);
            Text(x+14,482,230,32,g.basket[i]?"已放进购物袋":"按 "+(i+1)+" 或点击选择",17,Muted,false,TextAnchor.MiddleCenter);
            if(GUI.Button(new Rect(x,304,258,235),GUIContent.none,GUIStyle.none))g.Pick(i);
        }
        bool ready=g.basket[0]&&g.basket[1]&&g.basket[2];
        if(Button(393,610,812,66,ready?"买好了，准备回家  →":"把三样食材放进购物袋",true,ready))g.FinishShopping();
        if(Button(1096,174,109,39,"返回",false))g.panel="";
    }

    static void Home(SunnyGame g)
    {
        Backdrop();Panel(new Rect(395,148,810,604),Cream);
        Pill(437,185,160,"已到家 · 行程完成",SunnyWorld.Hex("DCEBD0"));
        Text(437,250,720,88,"今天的回家路，\n又好走了一点。",36,Ink,true);
        Text(437,369,720,41,"今天留下 "+g.tripReports+" 条反馈，沿途改善 "+g.tripRepairs+" 处通行问题。",23,Muted);
        Panel(new Rect(437,439,720,91),SunnyWorld.Hex("E5EDDA"));
        Text(460,452,670,61,"世界地图已保存   ·   "+g.TotalFixed()+" 处改善 / 75 处待改善地点",23,Teal,true,TextAnchor.MiddleCenter);
        if(Button(437,578,720,67,"看看城市地图，下一次去更远的地方  →")){g.selectedDistrict=g.district;g.panel="map";}
        Text(437,671,720,32,"修好的道路会留在这里，下次出门仍然可以使用。",18,Muted);
    }

    static void Map(SunnyGame g)
    {
        Backdrop();Panel(new Rect(80,70,1440,750),Cream);
        Text(120,100,900,58,"让每一条路，慢慢连起来。",36,Ink,true);
        Text(120,166,1000,36,"这台电脑上的城市  ·  25 个街区  ·  修复成果会持续保留",20,Muted);
        if(Button(1344,108,131,45,"关闭  M",false))g.panel=g.phase==2?"home":"";
        float gx=125,gy=246,step=99,side=83;
        for(int row=0;row<5;row++)for(int col=0;col<5;col++)
        {
            int i=row*5+col;float x=gx+col*step,y=gy+row*step;bool available=g.Available(i);int fixedCount=g.Count(g.save.repaired[i]);
            if(col<4&&g.save.repaired[i]==7&&g.save.repaired[i+1]==7)Rect(new Rect(x+side,y+39,16,7),Teal);
            if(row<4&&g.save.repaired[i]==7&&g.save.repaired[i+5]==7)Rect(new Rect(x+39,y+side,7,16),Teal);
            if(i==g.selectedDistrict)Panel(new Rect(x-4,y-4,side+8,side+8),Coral);
            Panel(new Rect(x,y,side,side),fixedCount==3?SunnyWorld.Hex("93D0AA"):available?SunnyWorld.Hex("D6E8C4"):SunnyWorld.Hex("ECEBDD"));
            Text(x+3,y+13,side-6,29,available?g.DistrictName(i):"待探索",16,available?Ink:Muted,available,TextAnchor.MiddleCenter);
            Text(x+3,y+48,side-6,23,available?fixedCount+" / 3":"·",14,Muted,false,TextAnchor.MiddleCenter);
            if(GUI.Button(new Rect(x,y,side,side),GUIContent.none,GUIStyle.none))g.selectedDistrict=i;
        }
        float rx=730;
        Text(rx,250,685,50,g.DistrictName(g.selectedDistrict),31,Ink,true);
        Text(rx,316,685,90,g.Available(g.selectedDistrict)?"走一趟自己的生活路线，\n也为这片街区留下一些改善。":"先完成邻近街区的出行，\n再从那里继续向外探索。",24,Muted);
        Panel(new Rect(rx,437,685,112),SunnyWorld.Hex("E9EFDE"));
        Text(rx+24,451,635,80,"已改善通行地点    "+g.TotalFixed()+" / 75\n已接通完整街区    "+g.ConnectedDistricts()+" / 25",23,Teal,true);
        bool canGo=g.Available(g.selectedDistrict)&&(g.phase==2||g.tripDistance<1);
        if(Button(rx,601,685,65,canGo?"从这里开始下一次出行  →":g.phase!=2&&g.tripDistance>=1?"先完成今天的行程，再去新街区":"这个街区还没有接通",true,canGo))g.StartSelected();
        Text(rx,697,685,62,"绿色片区之间的路会逐渐接通。\n每一局的改变，都会成为下一次出发的起点。",19,Muted);
    }

    static void Pause(SunnyGame g)
    {
        Backdrop();Panel(new Rect(520,225,560,443),Cream);Text(565,261,470,55,"在这里歇一会儿",32,Ink,true);
        if(Button(565,347,470,59,"继续走走"))g.panel="";
        if(Button(565,426,470,59,g.mute?"声音：关（点击开启）":"声音：开（点击关闭）",false))g.SetMute(!g.mute);
        if(Button(565,505,470,59,"保存并退出游戏",false)){g.Persist();Application.Quit();}
        Text(565,601,470,31,"F12 保存一张旅途照片",17,Muted);
    }
}
