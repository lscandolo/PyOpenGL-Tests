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

uniform float mat_bump_height;


void main(void)
{
  ex_Normal     = normalize(in_Modelview * vec4(in_Normal,0.0)).xyz;
  ex_Tangent    = normalize(in_Modelview * vec4(in_Tangent.xyz,0.0)).xyz;

  ex_Bitangent  = cross(in_Normal,in_Tangent.xyz);
  ex_Bitangent  = (in_Modelview * vec4(ex_Bitangent,0.0)).xyz;
  ex_Bitangent  = normalize(ex_Bitangent) * in_Tangent.w;

  ex_Position   = (in_Modelview * vec4(in_Position,1.0)).xyz;
  ex_TexCoord   = in_TexCoord;


  gl_Position = in_Projection * in_Modelview * vec4(in_Position, 1.0);

  /*Transf transforms from world space to tangent space
    (its transpose does the opposite)*/
  mat3 tbnTransf = transpose(mat3(ex_Tangent,ex_Bitangent,ex_Normal));
  tbnView = tbnTransf * ex_Position;

  /* We cannot normalize the tbnView vector here because it is in tangent space
   so the perspective correction that would be applied would not be correct*/
  
}
