// 3ds materials vertex shader

#version 140

uniform mat4 in_Modelview;
uniform mat4 in_Projection;

in  vec3 in_Position;
in  vec3 in_Normal;
in  vec2 in_TexCoord;
in  vec4 in_Tangent;

smooth out vec3 ex_Position;
smooth out vec3 ex_Normal;
smooth out vec2 ex_TexCoord;
smooth out vec3 ex_Tangent;
smooth out vec3 ex_Bitangent;

smooth out vec3 tbnView;
smooth out vec2 parallax;

void main(void)
{
  ex_Normal     = (in_Modelview * vec4(in_Normal,0.0)).xyz;
  ex_Tangent    = (in_Modelview * vec4(in_Tangent.xyz,0.0)).xyz;

  ex_Bitangent  = cross(in_Normal,in_Tangent.xyz);
  ex_Bitangent  = (in_Modelview * vec4(ex_Bitangent,0.0)).xyz;
  ex_Bitangent  = normalize(ex_Bitangent) * in_Tangent.w;

  ex_Position   = (in_Modelview * vec4(in_Position,1.0)).xyz;
  ex_TexCoord   = in_TexCoord;

  gl_Position = in_Projection * in_Modelview * vec4(in_Position, 1.0);

  /*Transf transforms from world space to tangent space
    (its transpose does the opposite)*/
  mat3 tbnTransf = transpose(mat3(ex_Tangent,ex_Bitangent,ex_Normal));
  tbnView = (tbnTransf * normalize(ex_Position));

  /*Initial parallax direction*/
  vec2 pllxDir = normalize(tbnView.xy);
  
  /*Length if parallax displacement vector*/
  float pllxLen = -sqrt(1 - tbnView.z * tbnView.z) / tbnView.z;

  /*Parallax bias allows control of parallax perspective via the 
   perpective_bias value*/
  float perspective_bias = 0;
  float pllxBias = perspective_bias + (1 - perspective_bias) * (2 * tbnView.z -1);
  
  /*Reverse Parallax displacement vector*/
  float height_scale = 0.02;
  vec2 parallax = -pllxDir * pllxLen * pllxBias * height_scale;

}
