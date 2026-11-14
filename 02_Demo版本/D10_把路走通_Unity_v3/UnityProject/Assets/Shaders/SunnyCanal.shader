Shader "Sunny/Canal"
{
 Properties { _Color ("Water",Color)=(0.25,0.7,0.73,1) }
 SubShader
 {
  Tags { "RenderType"="Opaque" }
  Pass
  {
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   struct v2f { float4 pos:SV_POSITION;float3 world:TEXCOORD0; };
   fixed4 _Color;
   v2f vert(appdata_base v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.world=mul(unity_ObjectToWorld,v.vertex).xyz;return o;}
   fixed4 frag(v2f i):SV_Target
   {
    float t=_Time.y;
    float wave=sin(i.world.z*11+sin(i.world.x*.5+t*.4)*.55+t*.7);
    float broken=smoothstep(.1,.5,sin(i.world.x*1.7+t*.24));
    float shimmer=smoothstep(.93,.995,wave)*broken;
    float broad=sin(i.world.z*1.2+sin(i.world.x*.16+t*.12))*.035;
    fixed3 c=lerp(_Color.rgb+float3(broad,broad,broad),float3(.76,.93,.87),shimmer*.52);
    return fixed4(c,1);
   }
   ENDCG
  }
 }
}
