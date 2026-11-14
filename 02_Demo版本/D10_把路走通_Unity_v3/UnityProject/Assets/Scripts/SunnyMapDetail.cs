using UnityEngine;

public static partial class SunnyUI
{
    static void CityGround(SunnyGame g)
    {
        Panel(new Rect(109,228,522,520),SunnyWorld.Hex("F1EEDD"));
        // A river occupies the gap between neighbourhoods; five bridges link both banks.
        for(int y=235;y<748;y+=6)
        {
            float x=412+Mathf.Sin((y-235)*.013f)*2.5f;
            Rect(new Rect(x,y,13,7),SunnyWorld.Hex("8DD6D1"));
        }
        float gx=125,gy=246,step=99,side=83;
        for(int row=0;row<5;row++)for(int col=0;col<5;col++)
        {
            int i=row*5+col;float x=gx+col*step,y=gy+row*step;
            if(col<4)
            {
                bool open=g.save.repaired[i]==7&&g.save.repaired[i+1]==7;
                Rect(new Rect(x+side,y+38,16,9),col==2?SunnyWorld.Hex("D4BF9C"):SunnyWorld.Hex("DDD5C0"));
                if(open)Rect(new Rect(x+side,y+41,16,3),Teal);
            }
            if(row<4)Rect(new Rect(x+38,y+side,9,16),SunnyWorld.Hex("DDD5C0"));
        }
    }

    static void RouteDetail(SunnyGame g,SunnyDistrict selected,float x,float y)
    {
        Text(x,y,685,29,"这次出行 · 沿晴溪向前",17,Muted);
        float lineY=y+61;
        Rect(new Rect(x+34,lineY,600,5),SunnyWorld.Hex("D6DBCB"));
        for(int i=0;i<5;i++)
        {
            float nx=x+34+i*150;bool fixedPoint=i>0&&i<4&&(g.save.repaired[selected.index]&(1<<(i-1)))!=0;
            Panel(new Rect(nx-8,lineY-6,18,18),i==0||i==4?Teal:fixedPoint?SunnyWorld.Hex("86C7A2"):Coral);
            string name=i==0?"家":i==4?selected.theme==0?"市集":selected.theme==1?"图书馆":"花园":selected.Issue(i-1).Replace("通道被","").Replace("人行道","").Replace("入口","");
            Text(nx-55,lineY+20,112,48,name,14,Muted,false,TextAnchor.UpperCenter);
        }
        Text(x,y+139,685,33,"累计 "+g.TotalFixed()+" / 75 处改善    ·    "+g.ConnectedDistricts()+" / 25 街区接通",20,Teal,true);
    }
}
