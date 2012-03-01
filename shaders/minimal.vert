// Vertex Shader – file "minimal.vert"

#version 330

uniform mat4 in_Modelview;
uniform mat4 in_Projection;

in  vec3 in_Position;
in  vec3 in_Normal;
in  vec2 in_TexCoord;

smooth out vec3 ex_Position;
smooth out vec3 ex_Normal;
smooth out vec3 ex_Color;
smooth out vec2 ex_TexCoord;
out float light_inc;

out vec3 light_source;

void main(void)
{

  light_source = (in_Modelview *  vec4(-0.707,-0.707,0.707,0.0)).xyz;

  /* float light_incidence = dot(normalize(in_Normal), light_source); */
  /* light_incidence = clamp(light_incidence,0,1); */

  /* light_inc = light_incidence; */

  /* ex_Color = vec3(1.0,1.0,1.0); */
  
  gl_Position = in_Projection * in_Modelview * vec4(in_Position, 1.0);

  /* ex_Normal = in_Normal; */
  ex_Normal = (in_Modelview * vec4(in_Normal,0.0)).xyz;

  ex_Position = (in_Modelview * vec4(in_Position,1.0)).xyz;

  ex_TexCoord = in_TexCoord;
}
