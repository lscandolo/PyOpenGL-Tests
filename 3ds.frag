#version 140

uniform mat4 in_Modelview;
uniform mat4 in_Projection;

smooth in vec3 ex_Color;
smooth in vec3 ex_Normal;
smooth in vec2 ex_TexCoord;
smooth in vec3 ex_Position;
smooth in vec3 ex_Tangent;
smooth in vec3 ex_Bitangent;


struct Texture3ds{
  bool      set;
  sampler2D tex;
  float     rotation;
  vec2      offset;
  vec2      scale;
  float     percent;
};

uniform Texture3ds texture1_map;
uniform Texture3ds texture2_map;
uniform Texture3ds opacity_map;
uniform Texture3ds bump_map;
uniform Texture3ds specular_map;
uniform Texture3ds shininess_map;
uniform Texture3ds self_illum_map;
uniform Texture3ds reflection_map;

uniform vec4  mat_ambient;
uniform vec4  mat_diffuse;
uniform vec4  mat_specular;
uniform float mat_shininess;
uniform float mat_shininess_strength;
uniform float mat_transparency;
uniform bool  mat_self_illum;
uniform float mat_self_ilpct;
uniform float mat_bump_size;

mat2 tex_rot(float r){
  return mat2(cos(r),sin(r),-sin(r),cos(r));
}

mat2 tex_scale(vec2 sc){
  return mat2(sc.s,0,0,sc.t);
}

vec2 tex_coords(Texture3ds map, vec2 coords){
  return tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset);
  /* return vec2(0.5) +  */
  /*   tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset-vec2(0.5)); */
}

/* vec2 tex_coords(Texture3ds map, vec2 coords){ */
/*   float a = radians(map.rotation); */
/*   float ca = cos(a); */
/*   float sa = sin(a); */
/*   float s0 = coords.s - map.offset.s  - 0.5; */
/*   /\* float t0 = 0.5 - coords.t - map.offset.t; *\/ */
/*   float t0 = coords.t - map.offset.t - 0.5; */
/*   float ss = ca * s0 - sa*t0; */
/*   float tt = sa * s0 + ca*t0; */
/*   ss = map.scale.s * ss + 0.5; */
/*   tt = map.scale.t * tt + 0.5; */
/*   return vec2(ss,tt); */
/* } */


void main(void)
{

  vec3  ambient;
  vec3  diffuse;
  vec3  specular;
  vec3  bump;
  float shininess;
  float shininess_strength;
  float transparency;
  float self_illum;
  float self_ilpct;
  float bump_size = mat_bump_size;

  if (texture1_map.set){
    vec2 coords = tex_coords(texture1_map,ex_TexCoord);
    ambient = texture2D(texture1_map.tex,coords).xyz * texture1_map.percent;
    if (texture2_map.set){
      coords = tex_coords(texture2_map,ex_TexCoord);
      ambient += texture2D(texture2_map.tex,coords).xyz * texture2_map.percent;
    }
    diffuse = ambient;
  }
  else{
    ambient = mat_ambient.xyz;
    diffuse = mat_diffuse.xyz;
  }

  if (specular_map.set){
    vec2 coords = tex_coords(specular_map,ex_TexCoord);
    specular = texture2D(specular_map.tex,coords).xyz * specular_map.percent;
  }
  else
    specular = mat_specular.xyz;

  if (shininess_map.set){
    vec2 coords = tex_coords(shininess_map,ex_TexCoord);
    shininess = texture2D(shininess_map.tex,coords).r * shininess_map.percent;
  }
  else
    shininess = mat_shininess;

  if (self_illum_map.set){
    vec2 coords = tex_coords(self_illum_map,ex_TexCoord);
    self_illum = texture2D(self_illum_map.tex,coords).r * self_illum_map.percent;
  }
  else
    self_illum = 0;

  self_ilpct = mat_self_ilpct;

  if (opacity_map.set){
    vec2 coords = tex_coords(opacity_map,ex_TexCoord);
    transparency = 1.0 - texture2D(opacity_map.tex,coords).r * opacity_map.percent;
  }
  else
    transparency = mat_transparency;

  vec3 normal = normalize(ex_Normal);

  if (bump_map.set){
    vec2 coords = tex_coords(bump_map,ex_TexCoord);
    bump =  texture2D(bump_map.tex,coords).xyz - vec3(0.5);
    mat3 transf = mat3(ex_Tangent,ex_Bitangent,ex_Normal);
    /* transf = transpose(transf); */
    bump = normalize(transf * bump);
    normal = bump;
  }
  else
    bump = vec3(0.0);

  vec3 light_source = normalize((in_Modelview *  vec4(0.707,0.707,0.707,0.0)).xyz);

  float ambient_strength;
  float diffuse_strength;

  ambient_strength = 0.4;
  diffuse_strength = 1.2;

  float diffuse_val = dot(normal, light_source);
  diffuse_val = clamp(diffuse_val,0,1);

  float specular_val;
  vec3 ref = reflect(-light_source,normal);
  specular_val = dot(-normalize(ex_Position),normalize(ref)); 
  specular_val = clamp(specular_val,0,1);
  specular_val = pow(specular_val, 16);

  vec3 color;
  color = ambient * (ambient_strength + self_illum);
  color += diffuse * diffuse_val * diffuse_strength;
  color += specular * specular_val /* * shininess */;

  gl_FragColor = vec4(color,1.0);
  gl_FragDepth = gl_FragCoord.z;


}
