// Fragment Shader – file "minimal.frag"

#version 140

precision highp float; // needed only for version 1.30

uniform mat4 in_Modelview;
uniform mat4 in_Projection;

smooth in vec3 ex_Color;
smooth in vec3 ex_Normal;
smooth in vec2 ex_TexCoord;
smooth in vec3 ex_Position;

in float light_inc;
in vec3 light_source;

uniform bool shininess_enabled;

//Textures!!

uniform sampler2D color_tex;
uniform sampler2D shininess_tex;

void main(void)
{
  float val = 0;
  if (dot(light_source,ex_Normal) > 0){
    vec3 ref = reflect(-normalize(light_source), normalize(ex_Normal));
    

    //Here position is the vector from the camera to the pixel, 
    //so we normalize it to get a versor pointing in the 
    //direction of the pixel
    val = dot(-normalize(ex_Position),ref); 

    if (shininess_enabled)
      val *= texture2D(shininess_tex,ex_TexCoord).r;

    val = clamp(val,0,1);
    val = pow(val, 16);
  }
  

  //	float val =  dot(normalize(-ex_Position) , normalize(ex_Normal));

  float light_inc = dot(normalize(ex_Normal), normalize(light_source));
  light_inc = clamp(light_inc,0,1);
  

  //Cartoon ?
  /* vec3 color = vec3(0.3,0.3,0.3); //-> Ambience */

  /* if (light_inc > 0.8){ */
  /*   color        += 0.5*ex_Color; //-> From directional light */
  /* } */
  /* else if (light_inc > 0.5){ */
  /*   color        += 0.3*ex_Color; //-> From directional light */
  /* } */
  /* else if (light_inc > 0.2){ */
  /*   color        += 0.1*ex_Color; //-> From directional light */
  /* } */

  /* if (val > 0.8) */
  /*   color        += vec3(1.0,0.0,0.0) * 0.8; // -> From shininess */
  /* else if (val > 0.5) */
  /*   color        += vec3(1.0,0.0,0.0) * 0.3; // -> From shininess */
  /* else if (val > 0.3) */
  /*   color        += vec3(1.0,0.0,0.0) * 0.1; // -> From shininess */


  //Normal

  vec2 tex_coord = vec2(ex_TexCoord.s,ex_TexCoord.t);

  vec3 color = texture2D(color_tex,tex_coord).rgb * 0.5;

  /* vec3 color = vec3(0.3,0.3,0.3); //-> Ambient */
  color        += light_inc * 0.3 * vec3(1.0,1.0,1.0); //-> From directional light
  color        += vec3(1.0,1.0,1.0) * val; // -> From shininess

  /* vec3 texval = texture(color_tex,ex_TexCoord).xyz; */

  /* if (texval.x == 0 && texval.y == 0 && texval.z == 0) */
  /*   color = vec3(1,0,0); */
  /* else */
  /*   color = vec3(0,0,1); */

  /* color += texture(tex,ex_TexCoord).xyz; */
  /* color += texture(tex,vec2(0.5,0)).xyz; */

  gl_FragColor = vec4(color, 1.0);
  /* gl_FragColor = texture(tex, ex_TexCoord.st); */


  /* gl_FragColor = vec4(1.0,1.0,1.0,1.0); */

  gl_FragDepth = gl_FragCoord.z;
}
