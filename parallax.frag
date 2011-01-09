#version 140

uniform mat4 in_Modelview;
uniform mat4 in_Projection;

smooth in vec3 ex_Color;
smooth in vec3 ex_Normal;
smooth in vec2 ex_TexCoord;
smooth in vec3 ex_Position;
smooth in vec3 ex_Tangent;
smooth in vec3 ex_Bitangent;


struct TextureMap{
  bool      set;
  sampler2D tex;
  float     rotation;
  vec2      offset;
  vec2      scale;
  float     percent;
};

struct TextureCubemap{
  bool        set;
  samplerCube tex;
  float       rotation;
};

uniform TextureMap texture1_map;
uniform TextureMap texture2_map;
uniform TextureMap opacity_map;
uniform TextureMap height_map;
uniform TextureMap normal_map;
uniform TextureMap specular_map;
uniform TextureMap shininess_map;
uniform TextureMap self_illum_map;
uniform TextureCubemap reflection_map;

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

vec2 tex_coords(TextureMap map, vec2 coords){
  return tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset);
}

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

  // Parallax mapping 
  if (height_map.set){
    float height_factor = 0.02;
    float bias_factor = 0.5;
    float h;

      /*Transf transforms from world space to tangent space
  	(its transpose does the opposite)*/
    mat3 transf = transpose(mat3(ex_Tangent,ex_Bitangent,ex_Normal));

    vec3 v = normalize(transf * (normalize(-ex_Position)));
    vec2 p;
    vec2 pn =  tex_coords(height_map,ex_TexCoord);

    //We iterate to get higher accuracy
    for (int i = 0; i < 3; i++){
      p = pn;
      h = texture2D(height_map.tex,p).x;
      h = (h - bias_factor) * height_factor;
      pn = p + (h * v.xy)/* /v.z */;
    }

    if (texture1_map.set){
      vec2 coords = pn;
      ambient = texture2D(texture1_map.tex,coords).xyz * texture1_map.percent;
      diffuse = ambient;
    }

    if (normal_map.set){
      vec2 coords = pn;
      vec3 new_normal =  texture2D(normal_map.tex,coords).xyz - vec3(0.5);
      new_normal = normalize(transpose(transf) * new_normal);
      normal = new_normal;
    }
  }

  if (reflection_map.set){
    mat3 transf = transpose(mat3(in_Modelview));
    vec3 ref = reflect(transf*ex_Position,transf*normal);
    ambient = texture(reflection_map.tex,ref).xyz;
    diffuse = ambient;
  }

  vec3 light_source = normalize((in_Modelview *  vec4(0.707,0.707,0.707,0.0)).xyz);

  float ambient_strength;
  float diffuse_strength;

  ambient_strength = 0.2;
  diffuse_strength = 0.7;

  float diffuse_val = dot(normal, light_source);
  diffuse_val = clamp(diffuse_val,0,1);

  float specular_val;

  vec3 ref = reflect(-light_source,normal);
  specular_val = dot(-normalize(ex_Position),normalize(ref)); 
  specular_val = clamp(specular_val,0,1);
  specular_val = pow(specular_val, 32);

  vec3 color;
  color = ambient * (ambient_strength + self_illum);
  color += diffuse * diffuse_val * diffuse_strength;
  color += specular * specular_val /* * shininess */;

  gl_FragColor = vec4(color,1.0);
  gl_FragDepth = gl_FragCoord.z;


}
