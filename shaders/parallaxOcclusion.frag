#version 140

/* Matrices */
uniform mat4 in_Modelview;
uniform mat4 in_ModelviewInv;
uniform mat4 in_View;
uniform mat4 in_Projection;

/* Geometry data */
smooth in vec3 ex_Color;
smooth in vec3 ex_Normal;
smooth in vec2 ex_TexCoord;
smooth in vec3 ex_Position;
smooth in vec3 ex_Tangent;
smooth in vec3 ex_Bitangent;
smooth in vec3 parallax;

/* Material variables */
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

/* Texture variables */
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

/* Light variables */
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
};

uniform AmbientLight ambient_light;
uniform int          spot_light_count;
uniform SpotLight    spot_light[10];


/* Texture functions*/
mat2 tex_rot(float r){
  return mat2(cos(r),sin(r),-sin(r),cos(r));
}

mat2 tex_scale(vec2 sc){
  return mat2(sc.s,0,0,sc.t);
}

vec2 tex_coords(TextureMap map, vec2 coords){
  return tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset);
}

/* Lighting functions */
vec3 reflected_light(vec3 f_col, vec3 f_pos, vec3 f_nor, float shininess){

  vec3 final_color = vec3(0,0,0);

  for (int i = 0; i < clamp(spot_light_count,0,10); i++){
    vec3 l_pos = (in_View * vec4(spot_light[i].position,1)).xyz;
    vec3 l_dir = normalize(mat3(in_View) * spot_light[i].direction).xyz;
    vec3 l_col = spot_light[i].color;

    vec3 lf_dir = normalize(f_pos-l_pos);

    float ang_dim = 1 - acos(dot(l_dir,lf_dir)) / (spot_light[i].aperture);
    float dist_dim = 1 - distance(l_pos,f_pos) / spot_light[i].reach;

    if (ang_dim > 1 || ang_dim < 0 || dist_dim < 0 || dist_dim > 1)
      continue;

    ang_dim = pow(ang_dim,spot_light[i].ang_dimming);
    dist_dim = pow(dist_dim,spot_light[i].dist_dimming);

    float diffuse_strength = dot(f_nor,-lf_dir);
    if (diffuse_strength < 0) continue;
    final_color += diffuse_strength*(l_col * f_col);
    
    vec3 reflection = reflect(lf_dir,f_nor);
    float specular_strength = dot(normalize(-f_pos),normalize(reflection));
    specular_strength = clamp(specular_strength,0,1);
    specular_strength = pow(specular_strength,spot_light[i].specular_exponent);
    specular_strength *= shininess;
    final_color += specular_strength * l_col;

    final_color *= ang_dim*dist_dim*spot_light[i].intensity;
  }

  if (spot_light_count > 0)
    final_color /= spot_light_count;
  return final_color;
}


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

  if (specular_map.set){
    vec2 coords = tex_coords(specular_map,ex_TexCoord);
    specular = texture2D(specular_map.tex,coords).xyz;
  }
  else
    specular = mat_specular.xyz;

  if (shininess_map.set){
    vec2 coords = tex_coords(shininess_map,ex_TexCoord);
    shininess = texture2D(shininess_map.tex,coords).r;
    shininess = clamp(shininess - 0.1,0,1);
  }
  else
    shininess = mat_shininess;

  if (self_illum_map.set){
    vec2 coords = tex_coords(self_illum_map,ex_TexCoord);
    self_illum = texture2D(self_illum_map.tex,coords).r;
  }
  else
    self_illum = 0;

  self_ilpct = mat_self_ilpct;

  if (opacity_map.set){
    vec2 coords = tex_coords(opacity_map,ex_TexCoord);
    transparency = 1.0 - texture2D(opacity_map.tex,coords).r;
  }
  else
    transparency = mat_transparency;

  vec3 normal = normalize(ex_Normal);

  // Parallax Occlusion Mapping
  if (height_map.set){

    const float maxheight = 1.0;
    float height_factor = mat_bump_height;

    const float minIter = 10;
    const float maxIter = 40;
    const float iterStep = 8;

    /* Texture vector corresponding plus height info*/
    vec3 tex_coords = vec3(tex_coords(height_map,ex_TexCoord),0);

    /*Iterations are a function of steepness : the more shallow, the more
     iterations we do to make sure we don't overshoot the bias by too much and
     we don't miss intersections */
    float linear_iterations = int(iterStep * length(parallax.xy));
    linear_iterations = clamp(linear_iterations,int(minIter),int(maxIter));

    /* Parallax step direction to traverse the heightmap */
    vec3 pllxStep = parallax / float(linear_iterations);
    pllxStep.xy *= height_factor;

    float h = (texture2D(height_map.tex,tex_coords.xy).x - 1) * maxheight;


    /* Linear search*/
    int i = 0;
    for (; i < linear_iterations; i++){
      tex_coords += pllxStep;
      h = (texture2D(height_map.tex,tex_coords.xy).x - 1) * maxheight;
      if (tex_coords.z < h) break;
    }
    /*-----------------------*/

    /* Secant method (one step)*/
    vec3 p0 = tex_coords - pllxStep;
    float h0 = (texture2D(height_map.tex,p0.xy).x - 1) * maxheight;
    float a = (h0 - p0.z) / (pllxStep.z - (h-h0));
    tex_coords = p0 + a * pllxStep;
    /*-------------------------*/

    if (texture1_map.set){
      ambient = texture2D(texture1_map.tex,tex_coords.xy).xyz 
	* texture1_map.percent;
      diffuse = ambient;
    }
    
    if (normal_map.set){
      normal =  texture2D(normal_map.tex,tex_coords.xy).xyz - vec3(0.5);
      normal = mat3(ex_Tangent,ex_Bitangent,ex_Normal) * normal;
      normal = normalize(normal);
    }
  }

  if (reflection_map.set){
    mat3 transf = mat3(in_ModelviewInv);
    vec3 ref = reflect(transf*ex_Position,transf*normal);
    ambient += texture(reflection_map.tex,ref).xyz * reflection_map.percent;
    diffuse  = ambient;
  }

  vec3 spot_color = reflected_light(diffuse, ex_Position, normal, shininess);

  vec3 ambient_color = ambient_light.intensity * normalize(ambient_light.color);
  ambient_color *= ambient;



  vec3 color = spot_color + ambient_color;

  gl_FragColor = vec4(color,transparency);
  gl_FragDepth = gl_FragCoord.z;


}
