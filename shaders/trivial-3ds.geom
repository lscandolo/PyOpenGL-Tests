// Geometry Shader – file "trivial-tri.geom"
#version 330

precision highp float;

uniform mat4 in_Modelview;
uniform mat4 in_ModelviewInv;
uniform mat4 in_Projection;

smooth in vec3 ex_Position[];
smooth in vec3 ex_Normal[];
smooth in vec2 ex_TexCoord[];
smooth in vec3 ex_Tangent[];
smooth in vec3 ex_Bitangent[];
smooth in vec3 ex_tbnView[];

smooth out vec3 Position;
smooth out vec3 Normal;
smooth out vec2 TexCoord;
smooth out vec3 Tangent;
smooth out vec3 Bitangent;
smooth out vec3 tbnView;

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;


struct TextureMap{
  bool      set;
  sampler2D tex;
  float     rotation;
  vec2      offset;
  vec2      scale;
  float     percent;
};

uniform TextureMap height_map;


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

void main(void)
{
	float h_mult = 0.3f;

	for (int i = 0; i < 3; ++i) {
		gl_Position = gl_in[i].gl_Position;
		Position   = ex_Position[i];
		Normal     = ex_Normal[i];
		TexCoord   = ex_TexCoord[i];
		Tangent    = ex_Tangent[i];
		Bitangent  = ex_Bitangent[i];
		tbnView    = ex_tbnView[i];

		EmitVertex();
	}
	EndPrimitive();
}
