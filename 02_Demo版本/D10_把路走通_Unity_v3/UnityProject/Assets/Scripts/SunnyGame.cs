using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

[Serializable] public sealed class SunnySave
{
    public int version=3;
    public int[] repaired=new int[25];
    public int[] pending=new int[25];
    public int[] visits=new int[25];
    public int district=12;
    public int[] seenStory=new int[25];
    public List<SunnyRecord> records=new List<SunnyRecord>();
}

public sealed partial class SunnyGame : MonoBehaviour
{
    public static SunnyGame Instance;
    public SunnySave save;
    public int district=12;
    public int phase; // 0 outbound, 1 returning, 2 home
    public string panel="title";
    public int reportIndex=-1;
    public bool[] basket=new bool[3];
    public Transform player, visual;
    public CharacterController controller;
    public Camera cam;
    public SunnyWorld world;
    public Vector2 testInput;
    public bool testDriving;
    public bool mute;
    public float distanceTravelled;
    public float tripDistance;
    public int tripReports;
    public int tripRepairs;
    public string lastMessage="";
    public float toastUntil;
    public int selectedDistrict=12;
    readonly List<Transform> wheels=new List<Transform>();
    readonly List<Transform> residents=new List<Transform>();
    readonly List<Vector3> residentBases=new List<Vector3>();
    Vector3 cameraVelocity;
    Vector3 velocity;
    float verticalSpeed;
    float facing=1;
    bool repairing;
    AudioSource audioSource, ambience;
    AudioClip chime;
    float elapsed;
    public const string SaveKey="SunnyPath_World_v3";

    void Awake()
    {
        Instance=this;Application.targetFrameRate=60;Application.runInBackground=true;
        QualitySettings.vSyncCount=1;
        Load();district=save.district;
        MakeAudio();SetupLighting();BuildDistrict(district);
        var args=Environment.GetCommandLineArgs();
        if(Array.IndexOf(args,"--smoke-test")>=0)StartCoroutine(StandaloneSmoke());
    }

    void Load()
    {
        try{save=JsonUtility.FromJson<SunnySave>(PlayerPrefs.GetString(SaveKey,""));}catch{save=null;}
        if(save==null||save.version!=3||save.repaired==null||save.repaired.Length!=25||save.pending==null||save.pending.Length!=25||save.visits==null||save.visits.Length!=25)save=new SunnySave();
        save.version=3;if(save.seenStory==null||save.seenStory.Length!=25)save.seenStory=new int[25];if(save.records==null)save.records=new List<SunnyRecord>();
        save.district=Mathf.Clamp(save.district,0,24);
        for(int i=0;i<25;i++){save.repaired[i]&=7;save.pending[i]&=7;}
    }

    public void Persist(){save.district=district;PlayerPrefs.SetString(SaveKey,JsonUtility.ToJson(save));PlayerPrefs.Save();}

    void SetupLighting()
    {
        RenderSettings.ambientMode=AmbientMode.Trilight;
        RenderSettings.ambientSkyColor=SunnyWorld.Hex("B6CFD4").linear;
        RenderSettings.ambientEquatorColor=SunnyWorld.Hex("8BA9A7").linear;
        RenderSettings.ambientGroundColor=SunnyWorld.Hex("82957D").linear;
        RenderSettings.ambientIntensity=.85f;
        RenderSettings.fog=true;RenderSettings.fogColor=SunnyWorld.Hex("D8EBDA");
        RenderSettings.fogMode=FogMode.Linear;RenderSettings.fogStartDistance=55;RenderSettings.fogEndDistance=145;
        var sun=new GameObject("AfternoonSun").AddComponent<Light>();sun.type=LightType.Directional;
        sun.color=SunnyWorld.Hex("FFF4DF");sun.intensity=1.02f;
        sun.transform.rotation=Quaternion.Euler(48,-35,0);sun.shadows=LightShadows.Soft;sun.shadowStrength=.40f;sun.shadowBias=.035f;
        QualitySettings.shadowDistance=45;QualitySettings.shadows=ShadowQuality.All;QualitySettings.shadowResolution=ShadowResolution.Medium;
        var cameraObject=new GameObject("MainCamera");cam=cameraObject.AddComponent<Camera>();cameraObject.tag="MainCamera";
        cam.orthographic=false;cam.fieldOfView=33;cam.orthographicSize=4.7f;cam.nearClipPlane=.1f;cam.farClipPlane=140;
        cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=SunnyWorld.Hex("AEE1E6");
        cameraObject.AddComponent<AudioListener>();
    }

    public void BuildDistrict(int index)
    {
        repairing=false;
        if(world!=null)world.Dispose();if(player)Destroy(player.gameObject);
        foreach(var r in residents)if(r)Destroy(r.gameObject);
        residents.Clear();residentBases.Clear();wheels.Clear();
        district=index;selectedDistrict=index;phase=0;tripReports=0;tripRepairs=0;tripDistance=0;
        distanceTravelled=0;verticalSpeed=0;basket=new bool[3];facing=1;velocity=Vector3.zero;
        config=SunnyDistrict.Make(index);selectedBook=-1;taskStep=0;storyIndex=-1;taskFeedback="";
        world=new SunnyWorld();world.Build(index,save.repaired[index]);
        player=new GameObject("WheelchairPlayer").transform;player.position=new Vector3(3,.05f,0);
        controller=player.gameObject.AddComponent<CharacterController>();
        controller.radius=.47f;controller.height=1.65f;controller.center=new Vector3(0,.84f,0);
        controller.stepOffset=.09f;controller.slopeLimit=25;controller.skinWidth=.035f;controller.minMoveDistance=0;
        visual=world.Asset("Hero",Vector3.zero,1,0,player).transform;
        GroupWheels();
        ResetViewRig();
        SpawnNeighbours();
        if(world.gardenPlant&&save.visits[index]>0)world.gardenPlant.localScale=Vector3.one*.9f;
        cam.backgroundColor=SunnyWorld.Hex(config.sky);
        cam.transform.position=new Vector3(6,4.8f,-18.5f);
        cam.transform.rotation=Quaternion.LookRotation(new Vector3(5,1.1f,0)-cam.transform.position);
        cameraVelocity=Vector3.zero;
        Persist();
    }

    public void Begin(){panel="";Toast(config.taskTitle+"，沿路看看通行情况。",5);}

    void GroupWheels()
    {
        var all=visual.GetComponentsInChildren<Transform>();
        foreach(var center in all)
        {
            bool rear=center.name.Contains("WheelRear"),front=center.name.Contains("WheelFront");
            if(!rear&&!front)continue;
            var pivot=new GameObject("RollingWheel").transform;pivot.SetParent(visual,false);
            pivot.position=center.position;pivot.rotation=visual.rotation;
            foreach(var part in all)
            {
                bool match=rear?(part.name.Contains("WheelRear")||part.name.Contains("WheelHub")||part.name.Contains("WheelCenter")||part.name.Contains("PushRing")||part.name.Contains("Spoke")):(part.name.Contains("WheelFront")||part.name.Contains("FrontHub"));
                if(match&&Mathf.Abs(part.position.z-center.position.z)<.19f&&Vector3.Distance(part.position,center.position)<(rear?.5f:.2f))part.SetParent(pivot,true);
            }
            wheels.Add(pivot);
        }
    }

    void Update()
    {
        elapsed+=Time.deltaTime;
        if(Input.GetKeyDown(KeyCode.F12))Capture();
        if(Input.GetKeyDown(KeyCode.Escape))
        {
            if(panel=="")panel="pause";
            else if(panel=="map")panel=phase==2?"home":"";
            else if(panel=="report"||panel=="shop"||panel=="pause"||panel=="story"||panel=="journal")panel="";
            else if(panel=="home")panel="map";
        }
        if(Input.GetKeyDown(KeyCode.M)&&panel!="title"&&panel!="report"&&panel!="shop")
        {selectedDistrict=district;panel=panel=="map"?(phase==2?"home":""):"map";}
        if(Input.GetKeyDown(KeyCode.E))Interact();
        if(Input.GetKeyDown(KeyCode.J)&&panel!="title"&&panel!="report"&&panel!="shop")panel=panel=="journal"?"":"journal";
        if(panel=="")cameraFov=Mathf.Clamp(cameraFov-Input.mouseScrollDelta.y*1.8f,25,36);
        if(Input.GetKeyDown(KeyCode.Return))
        {
            if(panel=="title")Begin();else if(panel=="report")SubmitReport();
            else if(panel=="shop"&&basket[0]&&basket[1]&&basket[2])FinishShopping();
        }
        if(panel=="shop")
        {if(Input.GetKeyDown(KeyCode.Alpha1))Pick(0);if(Input.GetKeyDown(KeyCode.Alpha2))Pick(1);if(Input.GetKeyDown(KeyCode.Alpha3))Pick(2);}
        if(panel==""&&!repairing)Move();
        UpdateViewInput();
        AnimateResidents();
    }

    int NearbyIssue()
    {
        if(!player)return -1;
        int best=-1;float nearest=5.8f;
        for(int i=0;i<3;i++)
        {float d=Mathf.Abs(player.position.x-config.positions[i]);if(d<nearest){nearest=d;best=i;}}
        return best;
    }

    public void Interact()
    {
        if(panel=="title"){Begin();return;}
        if(panel=="report"){SubmitReport();return;}
        if(panel=="story"){CloseStory();return;}
        if(panel!=""||repairing)return;
        if(phase==1&&player.position.x<6){ArriveHome();return;}
        if(phase==0&&player.position.x>config.destination-6){panel="shop";Chime(1);return;}
        int i=NearbyIssue();if(i<0){int story=NearbyStory();if(story>=0){storyIndex=story;panel="story";Chime(.8f);}return;}
        if((save.repaired[district]&(1<<i))!=0){Toast("这里已经修好，可以直接通行了。",3);return;}
        if((save.pending[district]&(1<<i))!=0){Toast("已收到这处反馈，先去完成今天的事吧。",3);return;}
        reportIndex=i;SunnyUI.RecordFrame(cam);panel="report";Chime(.7f);
    }

    public void SubmitReport()
    {
        if(reportIndex<0||reportIndex>2)return;
        int bit=1<<reportIndex;
        if((save.pending[district]&bit)==0&&(save.repaired[district]&bit)==0)
        {save.pending[district]|=bit;tripReports++;AddRecord(reportIndex);Persist();}
        panel="";Toast("城市服务已接收："+config.Issue(reportIndex)+"。可以继续出发了。",4.5f);Chime(1.2f);
    }

    public void Pick(int i)
    {
        if(i<0||i>2||basket[i])return;
        if(config.theme!=0&&i>0&&!basket[i-1]){TaskHint("先完成前一步，再继续吧。");return;}
        basket[i]=true;taskStep=i+1;taskFeedback="";Chime(1.1f+i*.16f);
        if(config.theme==1&&i==1)selectedBook=1;
        if(config.theme==2&&world.gardenPlant&&i>=1)world.gardenPlant.localScale=Vector3.one*(i==1?.75f:1.0f);
    }

    public void FinishShopping()
    {
        if(panel!="shop"||!basket[0]||!basket[1]||!basket[2]||repairing)return;
        panel="";phase=1;if(config.theme==0)AddBag();else if(config.theme==1)world.Asset("Book",new Vector3(.08f,.83f,0),.7f,0,visual);StartCoroutine(RepairSequence());
    }

    IEnumerator RepairSequence()
    {
        repairing=true;Toast(config.theme==0?"买好啦！城市服务正在处理沿途反馈……":config.theme==1?"借好书了！城市服务正在处理沿途反馈……":"薄荷种好了！城市服务正在处理沿途反馈……",4);
        yield return new WaitForSeconds(1.0f);
        int pending=save.pending[district];
        for(int i=0;i<3;i++)if((pending&(1<<i))!=0)
        {
            world.SetRepaired(i,true);save.repaired[district]|=1<<i;save.pending[district]&=~(1<<i);tripRepairs++;
            CompleteRecord(i);Confetti(new Vector3(config.positions[i],.4f,0));Chime(1+i*.18f);Persist();
            yield return new WaitForSeconds(.65f);
        }
        repairing=false;facing=-1;
        Toast(tripRepairs>0?"沿途的 "+tripRepairs+" 处问题已修复。回家时走走看！":"今天的事办好了，沿原路回家吧。",5);
    }

    void AddBag()
    {
        var bag=world.Box("ShoppingBag",new Vector3(-.6f,.72f,.38f),new Vector3(.26f,.34f,.25f),"BD8053",false,visual);
        world.Box("BagHandles",new Vector3(-.6f,.95f,.38f),new Vector3(.16f,.13f,.06f),"FFC94D",false,visual);
        world.Box("CarrotTops",new Vector3(-.6f,.96f,.4f),new Vector3(.11f,.16f,.13f),"62BC65",false,visual);
    }

    public void ArriveHome()
    {
        if(phase!=1)return;
        phase=2;save.visits[district]++;Persist();panel="home";Chime(1.35f);
        Confetti(player.position+Vector3.up*.5f);
    }

    void MakeAudio()
    {
        audioSource=gameObject.AddComponent<AudioSource>();audioSource.volume=.22f;
        chime=AudioClip.Create("SoftMarimba",11025,1,22050,false);var wave=new float[11025];
        for(int i=0;i<wave.Length;i++){float t=i/22050f;wave[i]=(Mathf.Sin(t*2*Mathf.PI*660)+.28f*Mathf.Sin(t*2*Mathf.PI*1320))*Mathf.Exp(-t*11)*.34f;}
        chime.SetData(wave,0);
        ambience=gameObject.AddComponent<AudioSource>();ambience.loop=true;ambience.volume=.045f;
        var clip=AudioClip.Create("SunnyAir",22050*12,1,22050,false);var air=new float[22050*12];
        for(int i=0;i<air.Length;i++)
        {
            float t=i/22050f;float chirp=Mathf.Pow(Mathf.Max(0,Mathf.Sin(t*2.1f)),16)*Mathf.Pow(Mathf.Max(0,Mathf.Sin(t*17)),5);
            air[i]=Mathf.Sin(t*2*Mathf.PI*(1900+250*Mathf.Sin(t*27)))*chirp*.30f;
        }
        clip.SetData(air,0);ambience.clip=clip;ambience.Play();
    }

    public void Chime(float pitch){if(!mute){audioSource.pitch=pitch;audioSource.PlayOneShot(chime);}}
    public void SetMute(bool value){mute=value;ambience.mute=value;}
    public void Toast(string message,float duration=4){lastMessage=message;toastUntil=Time.unscaledTime+duration;}
    public int Count(int mask){int n=0;for(int i=0;i<3;i++)if((mask&(1<<i))!=0)n++;return n;}
    public int TotalFixed(){int n=0;foreach(int m in save.repaired)n+=Count(m);return n;}
    public int ConnectedDistricts(){int n=0;foreach(int m in save.repaired)if(m==7)n++;return n;}
    public bool Available(int i)
    {
        if(i==12||i==13||i==11||save.visits[i]>0||save.repaired[i]>0||save.pending[i]>0)return true;
        int x=i%5,y=i/5;
        for(int j=0;j<25;j++)if(save.visits[j]>0&&Mathf.Abs(j%5-x)+Mathf.Abs(j/5-y)==1)return true;
        return false;
    }
    public string DistrictName(int i)
    {
        string[] a={"海风","晴日","向阳","花园","云朵"};string[] b={"街","里","坊","路","湾"};
        return i==12?"向阳里":i==7?"梧桐里":a[i%5]+b[i/5];
    }

    public void StartSelected()
    {
        if(!Available(selectedDistrict))return;
        panel="";BuildDistrict(selectedDistrict);Toast("从"+DistrictName(district)+"出发，"+config.taskTitle+"。",4);
    }

    public void Capture()
    {
        string dir=Application.isEditor?Path.GetFullPath(Path.Combine(Application.dataPath,"../../QA")):Path.Combine(Application.dataPath,"../Screenshots");
        Directory.CreateDirectory(dir);ScreenCapture.CaptureScreenshot(Path.Combine(dir,"play_"+DateTime.Now.ToString("yyyyMMdd_HHmmss")+".png"));Toast("照片已保存。",2);
    }

    void Confetti(Vector3 p){StartCoroutine(ConfettiRoutine(p));}
    IEnumerator ConfettiRoutine(Vector3 p)
    {
        var bits=new List<GameObject>();var rng=new System.Random(87);
        for(int i=0;i<14;i++)
        {
            var o=world.Box("Celebration",p,new Vector3(.08f,.17f,.04f),i%2==0?"FFC94D":"F57857");bits.Add(o);
        }
        float t=0;while(t<1.5f)
        {
            t+=Time.deltaTime;
            for(int i=0;i<bits.Count;i++)if(bits[i])
            {float a=i*2.4f;bits[i].transform.position=p+new Vector3(Mathf.Cos(a)*t,2*t-1.2f*t*t,Mathf.Sin(a)*t);bits[i].transform.Rotate(100*Time.deltaTime,80*Time.deltaTime,0);}
            yield return null;
        }
        foreach(var o in bits)if(o)Destroy(o);
    }

    void OnApplicationQuit(){if(save!=null)Persist();}

    // UI and build smoke checks are implemented in the other partial source file.
    void OnGUI(){DrawInterface();}
    void DrawInterface(){SunnyUI.Draw(this);}

    IEnumerator StandaloneSmoke()
    {
        while(!UnityEngine.Rendering.SplashScreen.isFinished)yield return null;
        yield return new WaitForSeconds(1.5f);
        yield return new WaitForSeconds(1);
        SetFirstPerson(false);panel="";testDriving=true;testInput=Vector2.right;
        float start=player.position.x;yield return new WaitForSeconds(1);
        testDriving=false;testInput=Vector2.zero;
        string dir=Path.GetFullPath(Path.Combine(Application.dataPath,"../../QA"));Directory.CreateDirectory(dir);
        bool moved=player.position.x>start+1;
        File.WriteAllText(Path.Combine(dir,"standalone_smoke.json"),JsonUtility.ToJson(new SmokeResult{moved=moved,heroRenderers=visual.GetComponentsInChildren<Renderer>().Length,obstacles=3,districts=25,themes=3},true));
        ScreenCapture.CaptureScreenshot(Path.Combine(dir,"standalone_smoke.png"));
        yield return new WaitForSeconds(.5f);
        var priorSave=save;int priorDistrict=district;
        save=new SunnySave();
        foreach(int index in new[]{12,13,11})
        {
            SetFirstPerson(false);BuildDistrict(index);panel="";controller.enabled=false;
            player.position=new Vector3(config.positions[0]-5.2f,.04f,0);controller.enabled=true;
            SetFirstPerson(true);yield return new WaitForSeconds(.9f);
            ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_first_person_"+config.theme+".png"));
            yield return new WaitForSeconds(.35f);SetFirstPerson(false);controller.enabled=false;
            player.position=new Vector3(config.destination-2,.04f,0);controller.enabled=true;
            cam.transform.position=new Vector3(Mathf.Min(96,config.destination),4.8f,-18.5f);
            cam.transform.rotation=Quaternion.LookRotation(new Vector3(cam.transform.position.x,1.15f,.1f)-cam.transform.position);
            cameraVelocity=Vector3.zero;
            yield return new WaitForSeconds(1.1f);
            ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_theme_"+config.theme+"_scene.png"));
            yield return new WaitForSeconds(.35f);
            panel="shop";Pick(0);Pick(1);if(config.theme!=1)Pick(2);
            yield return new WaitForSeconds(.5f);
            ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_theme_"+config.theme+"_task.png"));
            yield return new WaitForSeconds(.35f);
        }
        SetFirstPerson(false);BuildDistrict(12);panel="";controller.enabled=false;
        player.position=new Vector3(30,.04f,0);controller.enabled=true;cameraFov=25;
        yield return new WaitForSeconds(1);ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_neighbours.png"));yield return new WaitForSeconds(.4f);
        controller.enabled=false;player.position=new Vector3(world.bridgeX,.04f,-14);controller.enabled=true;
        SetFirstPerson(true);viewYaw=-90;viewPitch=7;yield return new WaitForSeconds(1.1f);
        ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_bridge_first_person.png"));yield return new WaitForSeconds(.4f);
        panel="map";selectedDistrict=12;ScreenCapture.CaptureScreenshot(Path.Combine(dir,"native_city_map.png"));yield return new WaitForSeconds(.4f);
        save=priorSave;district=priorDistrict;Persist();Application.Quit();
    }
    [Serializable] public class SmokeResult{public bool moved;public int heroRenderers,obstacles,districts,themes;}
}
