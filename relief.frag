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
  /* return vec2(0.5) +  */
  /*   tex_scale(map.scale)*tex_rot(map.rotation)*(coords-map.offset-vec2(0.5)); */
}

vec2 secant(vec2  x0, vec2 x1,
	    float z0, float z1,
	    float bias_factor, float height_factor,
	    sampler2D height, vec3 vdir){

  float iterations = 5;

  vec2 x2;
  float z2;

  float h0 = texture(height,x0).x;
  float h1 = texture(height,x1).x;
  float h2;
  vec3 hdir;

  float a;

  do {
    hdir = normalize( vec3(x1.x,x1.y,h1) - vec3(x0.x,x0.y,h0) );
    a = (h0 - z0) / (vdir.z - hdir.z);
    x2 = x0 + vdir.xy * a;
    z2 = z0 + vdir.z  * a;
    h2 = (texture(height,x2).x - bias_factor) * height_factor;

    x0 = x1;
    z0 = z1;
    x1 = x2;
    z1 = z2;
    h0 = h1;
    h1 = h2;

    iterations--;
  } 
  while (abs(h2 - z2) > 0.01 && iterations > 0) ;

  return x2;
}

vec2 bisection(vec3  x0, vec3 x1,
	       float bias_factor, float height_factor,
	       sampler2D height, vec3 vdir){
  vec3 x2;
  float h0 = texture(height,x0.xy).x;
  float h1 = texture(height,x1.xy).x;
  float h2;

  float iterations = 20;
  
  do{
    x2 = x0 + 0.5 * (x1 - x0);
    h2 = (texture(height,x2.xy).x - bias_factor) * height_factor;

    if (h2 < x2.z){
      x0 = x2;
      h0 = h2;
    }
    else{
      x1 = x2;
      h1 = h2;
    }

    iterations--;
  }
  while (abs(h2 - x2.z) > 0.001 && iterations > 0) ;
  return x2.xy;
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

  // Normal Mapping
  /* if (normal_map.set){ */
  /*   vec2 coords = tex_coords(normal_map,ex_TexCoord); */
  /*   vec3 new_normal = texture2D(normal_map.tex,coords).xyz - vec3(0.5); */
  /*   /\*Transf transforms from tangent space to world space */
  /*     (its transpose does the opposite)*\/ */
  /*   mat3 transf = mat3(ex_Tangent,ex_Bitangent,ex_Normal); */
  /*   new_normal = normalize(transf * new_normal); */
  /*   normal = new_normal; */
  /* } */

  // Relief mapping
  if (height_map.set){
    float height_factor = 0.05;
    float bias_factor = 1.0;

      /*Transf transforms from world space to tangent space
  	(its transpose does the opposite)*/
    mat3 transf = transpose(mat3(ex_Tangent,ex_Bitangent,ex_Normal));

    vec3 v = normalize(transf * normalize(ex_Position));


    vec2 p = tex_coords(height_map,ex_TexCoord);;
    vec2 pn = p;

    int iterations = 32;

    /* iterations = int(clamp(-5.0/v.z,32.0,5.0)); */
    
    float step_size = (height_factor / -v.z) /  float(iterations);

    vec3 vstep = v * step_size;
    vec3 vtest = vec3(0.0);

    float h = texture2D(height_map.tex,pn).x;
    h = (h - bias_factor) * height_factor;

    while (vtest.z > h){
      
      vtest += vstep;
      pn = p + vtest.xy;
      h = texture2D(height_map.tex,pn).x;
      h = (h - bias_factor) * height_factor;
    }

    /* pn = secant(pn-vstep.xy, pn, */
    /* 		(vtest-vstep).z, vtest.z, */
    /* 		bias_factor,height_factor, */
    /* 		height_map.tex,v); */
    pn = bisection(vec3(pn-vstep.xy,(vtest-vstep).z),vec3(pn,vtest.z),
		   bias_factor,height_factor,
		   height_map.tex,v);
		   


    if (texture1_map.set){
      vec2 coords = pn;
      ambient = texture2D(texture1_map.tex,coords).xyz * texture1_map.percent;
      if (iterations <= 0) ambient = vec3(1,1,0);
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

  /* mat3 Modelview_trans = inverse(transpose(mat3(in_Modelview))); */
  /* vec3 light_source = normalize(Modelview_trans *  vec3(0.707,0.707,0.707)); */

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
