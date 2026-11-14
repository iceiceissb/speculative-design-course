using UnityEngine;
using UnityEngine.Rendering;

public sealed partial class SunnyGame
{
    public bool firstPerson;
    public float chairYaw;
    public float viewYaw,viewPitch=14;
    float viewBlend;
    Quaternion firstRotation;
    Renderer[] sitterRenderers;
    bool sitterHidden;
    public string ViewName { get { return firstPerson?"轮椅上的视角":"河对岸的视角"; } }
    public string MoveHelp { get { return firstPerson?"W/S 前进后退   A/D 转向   按住右键环顾   V 切换   E 互动   M 地图   J 记录":"A/D 沿街   W/S 绕行   V 坐到轮椅上   E 互动   M 地图   J 记录   滚轮拉近"; } }

    public void ToggleView()
    {
        if(panel!=""&&panel!="pause")return;
        SetFirstPerson(!firstPerson);
        Toast(firstPerson?"坐到轮椅上：W/S 行驶，A/D 转向，按住鼠标右键环顾。":"回到河对岸：A/D 沿街，W/S 绕行。",4);
    }

    public void SetFirstPerson(bool value)
    {
        firstPerson=value;
        chairYaw=visual?visual.eulerAngles.y:0;
        viewYaw=0;viewPitch=14;
        velocity=Vector3.zero;
        if(!value)ReleaseLook();
    }

    void ResetViewRig()
    {
        chairYaw=0;viewYaw=0;viewPitch=14;viewBlend=firstPerson?1:0;
        sitterRenderers=visual.GetComponentsInChildren<Renderer>();sitterHidden=false;
        SetSitterVisibility(firstPerson);
        ReleaseLook();
    }

    void ReleaseLook(){Cursor.lockState=CursorLockMode.None;Cursor.visible=true;}
    void OnDisable(){ReleaseLook();}

    void UpdateViewInput()
    {
        if(Input.GetKeyDown(KeyCode.V))ToggleView();
        bool look=firstPerson&&panel==""&&Input.GetMouseButton(1);
        Cursor.lockState=look?CursorLockMode.Locked:CursorLockMode.None;
        Cursor.visible=!look;
        if(look)
        {
            viewYaw=Mathf.Clamp(viewYaw+Input.GetAxisRaw("Mouse X")*2.3f,-100,100);
            viewPitch=Mathf.Clamp(viewPitch-Input.GetAxisRaw("Mouse Y")*1.7f,-37,55);
        }
        if(firstPerson&&panel==""&&Input.GetKeyDown(KeyCode.R)){viewYaw=0;viewPitch=14;}
    }

    void SetSitterVisibility(bool hide)
    {
        if(sitterRenderers==null)return;
        foreach(var r in sitterRenderers)
            if(r&&(r.name.StartsWith("GEO-Head")||r.name.StartsWith("GEO-Torso")||r.name.StartsWith("GEO-Person")))
                r.shadowCastingMode=hide?ShadowCastingMode.ShadowsOnly:ShadowCastingMode.On;
        sitterHidden=hide;
    }

    void Move()
    {
        Vector2 input=testDriving?testInput:new Vector2((Input.GetKey(KeyCode.D)||Input.GetKey(KeyCode.RightArrow)?1:0)-(Input.GetKey(KeyCode.A)||Input.GetKey(KeyCode.LeftArrow)?1:0),
            (Input.GetKey(KeyCode.W)||Input.GetKey(KeyCode.UpArrow)?1:0)-(Input.GetKey(KeyCode.S)||Input.GetKey(KeyCode.DownArrow)?1:0));
        input=Vector2.ClampMagnitude(input,1);
        Vector3 desired;
        if(firstPerson)
        {
            chairYaw+=input.x*80*Time.deltaTime;
            visual.localRotation=Quaternion.Euler(0,chairYaw,0);
            desired=visual.TransformDirection(Vector3.right)*input.y*(Input.GetKey(KeyCode.LeftShift)?3.5f:2.7f);
            if(Mathf.Abs(desired.x)>.1f)facing=desired.x>0?1:-1;
        }
        else
        {
            desired=new Vector3(input.x,0,input.y)*(Input.GetKey(KeyCode.LeftShift)?4.4f:3.4f);
            if(Mathf.Abs(input.x)>.05f)facing=input.x>0?1:-1;
            var goal=Quaternion.Euler(0,facing<0?180:0,0);
            visual.localRotation=Quaternion.Slerp(visual.localRotation,goal,Time.deltaTime*8);
            chairYaw=visual.eulerAngles.y;
        }
        velocity=Vector3.MoveTowards(velocity,desired,Time.deltaTime*9);
        verticalSpeed=controller.isGrounded?-1.5f:Mathf.Max(verticalSpeed-22*Time.deltaTime,-12);
        var before=player.position;
        var horizontal=LimitChairMotion(velocity*Time.deltaTime);
        controller.Move(horizontal+Vector3.up*verticalSpeed*Time.deltaTime);
        var constrained=world.ConstrainPosition(player.position);
        if((constrained-player.position).sqrMagnitude>.000001f)
        {controller.enabled=false;player.position=constrained;controller.enabled=true;}
        var delta=player.position-before;delta.y=0;
        tripDistance+=delta.magnitude;distanceTravelled+=delta.magnitude;
        float rollDistance=Vector3.Dot(delta,visual.TransformDirection(Vector3.right));
        foreach(var wheel in wheels)wheel.Rotate(visual.TransformDirection(Vector3.forward),-rollDistance/.38f*Mathf.Rad2Deg,Space.World);
    }

    void LateUpdate()
    {
        if(!player||!cam)return;
        bool useFirst=firstPerson&&panel!="title";
        viewBlend=Mathf.MoveTowards(viewBlend,useFirst?1:0,Time.deltaTime*2.1f);
        float t=Mathf.SmoothStep(0,1,viewBlend);
        var sidePos=new Vector3(Mathf.Clamp(player.position.x+facing*2.1f,6,config.destination-1),4.9f,player.position.z-18.5f);
        if(panel=="title")sidePos.x=1;
        var sideRotation=Quaternion.LookRotation(new Vector3(sidePos.x,1.05f,player.position.z+.2f)-sidePos);
        var eye=player.position+visual.TransformDirection(new Vector3(-.25f,1.49f,0));
        firstRotation=Quaternion.Euler(viewPitch,90+chairYaw+viewYaw,0);
        var position=Vector3.Lerp(sidePos,eye,t);
        // A transition follows a predictable arc; the final seated view has no head bob.
        position.y+=Mathf.Sin(t*Mathf.PI)*.8f;
        cam.transform.position=Vector3.SmoothDamp(cam.transform.position,position,ref cameraVelocity,useFirst&&viewBlend>=1?.045f:.18f);
        cam.transform.rotation=Quaternion.Slerp(sideRotation,firstRotation,t);
        cam.fieldOfView=Mathf.Lerp(cameraFov,72,t);
        cam.nearClipPlane=Mathf.Lerp(.10f,.035f,t);
        bool hide=useFirst||viewBlend>.28f;
        if(hide!=sitterHidden)SetSitterVisibility(hide);
    }
}
