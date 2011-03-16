#version 330

/* ------------------- Matrices  -----------------------------*/
uniform mat4 in_Modelview;
uniform mat4 in_ModelviewInv;
uniform mat4 in_View;
uniform mat4 in_Projection;

/* --------------------- Geometry data --------------------*/
smooth in vec3 ex_Color;
smooth in vec3 ex_Normal;
smooth in vec2 ex_TexCoord;
smooth in vec3 ex_Position;
smooth in vec3 ex_Tangent;
smooth in vec3 ex_Bitangent;
smooth in vec3 tbnView;

/* -------------------- Material variables ----------------- */
uniform vec4  mat_ambient;
uniform vec4  mat_diffuse;
uniform vec4  mat_specular;
uniform float mat_shininess;
uniform float mat_shininess_strength;
uniform float mat_transparency;
uniform bool  mat_self_illum;
uniform float mat_self_ilpct;
uniform float mat_bump_height;
uniform float mat_bump_bias;

/* ---------------------- Texture variables -----------------------*/
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
  float       percent;
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

/*  -------------------------- Light variables ---------------- */
struct AmbientLight{
  float intensity;
  vec3  color;
};

struct SpotLight{
  float intensity;
  vec3  color;
  vec3  position;
  vec3  direction;
  float reach;
  float aperture;
  float dist_dimming;
  float ang_dimming;
  int   specular_exponent;
  bool  has_shadow_map;
  sampler2DShadow shadow_map; 
};

uniform AmbientLight ambient_light;
uniform SpotLight    spot_light[10];
uniform int          spot_light_count;


/* ----------------------- Texture functions -------------------*/
mat2 tex_rot(float r){
  return mat2(cos(r),sin(r),-sin(r),cos(r));
}

mat2 tex_scale(vec2 sc){
  return mat2(sc.s,0,0,sc.t);
}

vec2 tex_coords(TextureMap map, vec2 coords){
  return tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset);
}

const float minreach = 0.01;

/* ----------------  Lighting functions  --------------------- */
vec3 reflected_light(vec3 f_col, vec3 f_pos, vec3 f_nor, 
		     float shininess, int i){

  vec3 final_color = vec3(0,0,0);

  vec3 l_pos = (in_View * vec4(spot_light[i].position,1)).xyz;
  vec3 l_dir = normalize(mat3(in_View) * spot_light[i].direction).xyz;
  vec3 l_col = spot_light[i].color;
  vec3 lf_dir = normalize(f_pos-l_pos);

  float lf_cosang = dot(l_dir,lf_dir);
  float lf_dist   = distance(l_pos,f_pos);

  if (lf_cosang < 0 ||
      lf_cosang < cos(spot_light[i].aperture) ||
      lf_dist   > spot_light[i].reach)
    return final_color;

  float ang_dim = pow(lf_cosang-cos(spot_light[i].aperture),spot_light[i].ang_dimming);

  float dist_dim = 
    min(1,spot_light[i].reach - lf_dist / (spot_light[i].reach - minreach));
  
  float diffuse_strength = dot(f_nor,-lf_dir);
  if (diffuse_strength < 0) return final_color;
  final_color = diffuse_strength*(l_col * f_col);
    
  vec3 reflection = reflect(lf_dir,f_nor);
  float specular_strength = dot(normalize(-f_pos),normalize(reflection));
  specular_strength = clamp(specular_strength,0,1);
  specular_strength = pow(specular_strength,spot_light[i].specular_exponent);
  specular_strength *= shininess;
  final_color += specular_strength * l_col;

  final_color *= ang_dim*dist_dim*spot_light[i].intensity;
  return final_color;
}

/* -------------------------------- main -----------------------------*/
void main(void)
{
  vec3  ambient = vec3(mat_ambient);
  vec3  diffuse = vec3(mat_diffuse);
  vec3  specular;
  vec3  bump;
  float shininess;
  float shininess_strength;
  float transparency;
  float self_illum;
  float self_ilpct;

  specular = mat_specular.xyz;
  shininess = mat_shininess;
  self_illum = 0;
  self_ilpct = mat_self_ilpct;
  transparency = mat_transparency;

  vec2 tex_coords =  ex_TexCoord;
  vec3 normal = ex_Normal;

  ////--------------------Parallax Mapping if we have a height map
  /* if (false){ */
  if (height_map.set){
    float height_factor = mat_bump_height;
    float bias_factor = mat_bump_bias;
    float h;
    int iterations = 3;
    vec2 parallax = -normalize(tbnView).xy;
    tex_coords =  tex_coords(height_map,ex_TexCoord);

    //We iterate to get higher accuracy
    for (; iterations > 0; iterations--){
      h = texture(height_map.tex,tex_coords.xy).x;
      h = (h - bias_factor) * height_factor;
      tex_coords += (h * parallax);
    }

  }

  //// Color Texture retrieval
  if (texture1_map.set){
    ambient = texture(texture1_map.tex,tex_coords).xyz * texture1_map.percent;
    diffuse = ambient;
  }

  ////////// Normal mapping
  if (normal_map.set){
    normal =  texture(normal_map.tex,tex_coords).xyz - vec3(0.5,0.5,0.5);
    normal = mat3(ex_Tangent,ex_Bitangent,ex_Normal) * normal;
    normal = normalize(normal);
  }

  //////// Reflections
  if (reflection_map.set){
    mat3 transf = mat3(in_ModelviewInv);
    vec3 ref = reflect(transf*ex_Position,transf*normal);
    ambient += texture(reflection_map.tex,ref).xyz * reflection_map.percent;
    diffuse = ambient;
  }

  /////// Lighting computation
  vec3 spot_color = vec3(0.f);
  for (int l = 0; l < spot_light_count; l++){
    spot_color += reflected_light(diffuse, ex_Position, normal, shininess,l);
  }

  ////// Color adjusting
  vec3 ambient_color = ambient_light.intensity * normalize(ambient_light.color);
  ambient_color *= ambient;
  vec3 color = spot_color + ambient_color;

  /* float md = shadow2D(spot_light[0].shadow_map,vec3(ex_TexCoord,1)).x; */
  /* float md = texture(spot_light[0].shadow_map,ex_TexCoord).x; */
  /* float md = spot_light[0].direction.x; */
  float md = textureProj(spot_light[0].shadow_map,vec4(ex_TexCoord,0.5,0.5));
  color = vec3(md,md,md);

  gl_FragColor = vec4(color,transparency);
  gl_FragDepth = gl_FragCoord.z;

}


/* There are advanced techniques for */
/* smooth shadows */
/* » */
/* The most prominent are */
/* » */
/* » */
/* VSMs, layered VSMs, CSMs, ESMs, ACDF SMs */
/* Can be combined with SATs for arbitary */
/* smoothness */
