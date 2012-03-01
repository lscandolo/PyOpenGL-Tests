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
layout (triangle_strip, max_vertices = 11) out;

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


void output_5(float h_mult)
{

}

void output_11(float h_mult)
{
	output_5(h_mult);
}

void main(void)
{

	const float h_mult = 0.3f;
 
	const float far_dist = 5.f;
	const float close_dist = 3.f;


	vec3 PositionA, PositionB, PositionC;

	PositionA = ex_Position[0];
	PositionB = ex_Position[1];
	PositionC = ex_Position[2];

	vec2 a_coords = tex_coords(height_map,ex_TexCoord[0]);
	vec2 b_coords = tex_coords(height_map,ex_TexCoord[1]);
	vec2 c_coords = tex_coords(height_map,ex_TexCoord[2]);

	float a_height = texture(height_map.tex, a_coords).x;
	float b_height = texture(height_map.tex, b_coords).x;
	float c_height = texture(height_map.tex, c_coords).x;

	PositionA += ex_Normal[0] * h_mult * a_height;
	PositionB += ex_Normal[1] * h_mult * b_height;
	PositionC += ex_Normal[2] * h_mult * c_height;

	const float dist = length((PositionA + PositionB + PositionC)/3.f);

	/* ------------------------ Emit 3 vertices ---------------------------- */
	if (dist > far_dist) {


		/* Vertex A */
		gl_Position = in_Projection * vec4(PositionA,1.f);
		Position   = PositionA;
		Normal     = ex_Normal[0];
		TexCoord   = ex_TexCoord[0];
		Tangent    = ex_Tangent[0];
		Bitangent  = ex_Bitangent[0];
		tbnView    = ex_tbnView[0];
		EmitVertex();

		/* Vertex B */
		gl_Position = in_Projection * vec4(PositionB,1.f);
		Position   = PositionB;
		Normal     = ex_Normal[1];
		TexCoord   = ex_TexCoord[1];
		Tangent    = ex_Tangent[1];
		Bitangent  = ex_Bitangent[1];
		tbnView    = ex_tbnView[1];
		EmitVertex();

		/* Vertex C */
		gl_Position = in_Projection * vec4(PositionC,1.f);
		Position   = PositionC;
		Normal     = ex_Normal[2];
		TexCoord   = ex_TexCoord[2];
		Tangent    = ex_Tangent[2];
		Bitangent  = ex_Bitangent[2];
		tbnView    = ex_tbnView[2];
		EmitVertex();

		EndPrimitive();
    /*--------------------------- Emit 5 vertices ---------------------------------*/
	}       
	else if (dist > close_dist) {
		vec3 PositionD = (ex_Position[0] + ex_Position[1] + ex_Position[2]) / 3.f;

		vec3 d_Normal;
		vec2 d_TexCoord;
		vec3 d_Tangent;
		vec3 d_Bitangent;
		vec3 d_tbnView;

		d_Normal = (ex_Normal[0] + ex_Normal[1] + ex_Normal[2]) / 3.f;
		d_TexCoord = (ex_TexCoord[0] + ex_TexCoord[1] + ex_TexCoord[2]) / 3.f;
		d_Tangent = (ex_Tangent[0] + ex_Tangent[1] + ex_Tangent[2]) / 3.f;
		d_Bitangent = (ex_Bitangent[0] + ex_Bitangent[1] + ex_Bitangent[2]) / 3.f;
		d_tbnView = (ex_tbnView[0] + ex_tbnView[1] + ex_tbnView[2]) / 3.f;

		vec2 d_coords = tex_coords(height_map,d_TexCoord);
		float d_height = texture(height_map.tex, d_coords).x;
		PositionD += h_mult * d_height * d_Normal;
	
		/* Vertex A */
		gl_Position = in_Projection * vec4(PositionA,1.f);
		Position   = PositionA;
		Normal     = ex_Normal[0];
		TexCoord   = ex_TexCoord[0];
		Tangent    = ex_Tangent[0];
		Bitangent  = ex_Bitangent[0];
		tbnView    = ex_tbnView[0];
		EmitVertex();

		/* Vertex B */
		gl_Position = in_Projection * vec4(PositionB,1.f);
		Position   = PositionB;
		Normal     = ex_Normal[1];
		TexCoord   = ex_TexCoord[1];
		Tangent    = ex_Tangent[1];
		Bitangent  = ex_Bitangent[1];
		tbnView    = ex_tbnView[1];
		EmitVertex();

		/* Vertex D */
		gl_Position = in_Projection * vec4(PositionD,1.f);
		Position = PositionD;
		Normal = d_Normal;
		TexCoord = d_TexCoord;
		Tangent = d_Tangent;
		Bitangent = d_Bitangent;
		tbnView = d_tbnView;
		EmitVertex();

		/* Vertex C */
		gl_Position = in_Projection * vec4(PositionC,1.f);
		Position   = PositionC;
		Normal     = ex_Normal[2];
		TexCoord   = ex_TexCoord[2];
		Tangent    = ex_Tangent[2];
		Bitangent  = ex_Bitangent[2];
		tbnView    = ex_tbnView[2];
		EmitVertex();

		/* Vertex A */
		gl_Position = in_Projection * vec4(PositionA,1.f);
		Position   = PositionA;
		Normal     = ex_Normal[0];
		TexCoord   = ex_TexCoord[0];
		Tangent    = ex_Tangent[0];
		Bitangent  = ex_Bitangent[0];
		tbnView    = ex_tbnView[0];
		EmitVertex();

		EndPrimitive();
	}	
    /*--------------------------- Emit 5 vertices ---------------------------------*/
	else {

		// Vertex D
		vec3 PositionD = (ex_Position[0] + ex_Position[1] + ex_Position[2]) / 3.f;
		vec3 orig_PositionD = PositionD;

		vec3 d_Normal;
		vec2 d_TexCoord;
		vec3 d_Tangent;
		vec3 d_Bitangent;
		vec3 d_tbnView;

		d_Normal    = (ex_Normal[0]    + ex_Normal[1]    + ex_Normal[2])    / 3.f;
		d_TexCoord  = (ex_TexCoord[0]  + ex_TexCoord[1]  + ex_TexCoord[2])  / 3.f;
		d_Tangent   = (ex_Tangent[0]   + ex_Tangent[1]   + ex_Tangent[2])   / 3.f;
		d_Bitangent = (ex_Bitangent[0] + ex_Bitangent[1] + ex_Bitangent[2]) / 3.f;
		d_tbnView   = (ex_tbnView[0]   + ex_tbnView[1]   + ex_tbnView[2])   / 3.f;

		vec2 d_coords = tex_coords(height_map,d_TexCoord);
		float d_height = texture(height_map.tex, d_coords).x;
		PositionD += h_mult * d_height * d_Normal;

		// Vertex E
		vec3 PositionE = (ex_Position[0] + ex_Position[1] + orig_PositionD) / 3.f;

		vec3 e_Normal;
		vec2 e_TexCoord;
		vec3 e_Tangent;
		vec3 e_Bitangent;
		vec3 e_tbnView;

		e_Normal = (ex_Normal[0] + ex_Normal[1] + d_Normal) / 3.f;
		e_TexCoord = (ex_TexCoord[0] + ex_TexCoord[1] + d_TexCoord) / 3.f;
		e_Tangent = (ex_Tangent[0] + ex_Tangent[1] + d_Tangent) / 3.f;
		e_Bitangent = (ex_Bitangent[0] + ex_Bitangent[1] + d_Bitangent) / 3.f;
		e_tbnView = (ex_tbnView[0] + ex_tbnView[1] + d_tbnView) / 3.f;

		vec2 e_coords = tex_coords(height_map,e_TexCoord);
		float e_height = texture(height_map.tex, e_coords).x;
		PositionE += h_mult * e_height * e_Normal;

		// Vertex F
		vec3 PositionF = (ex_Position[0] + orig_PositionD + ex_Position[2]) / 3.f;

		vec3 f_Normal;
		vec2 f_TexCoord;
		vec3 f_Tangent;
		vec3 f_Bitangent;
		vec3 f_tbnView;

		f_Normal = (ex_Normal[0] + d_Normal + ex_Normal[2]) / 3.f;
		f_TexCoord = (ex_TexCoord[0] + d_TexCoord + ex_TexCoord[2]) / 3.f;
		f_Tangent = (ex_Tangent[0] + d_Tangent + ex_Tangent[2]) / 3.f;
		f_Bitangent = (ex_Bitangent[0] + d_Bitangent + ex_Bitangent[2]) / 3.f;
		f_tbnView = (ex_tbnView[0] + d_tbnView + ex_tbnView[2]) / 3.f;

		vec2 f_coords = tex_coords(height_map,f_TexCoord);
		float f_height = texture(height_map.tex, f_coords).x;
		PositionF += h_mult * f_height * f_Normal;

		// Vertex G
		vec3 PositionG = (orig_PositionD + ex_Position[1] + ex_Position[2]) / 3.f;

		vec3 g_Normal;
		vec2 g_TexCoord;
		vec3 g_Tangent;
		vec3 g_Bitangent;
		vec3 g_tbnView;

		g_Normal = (d_Normal + ex_Normal[1] + ex_Normal[2]) / 3.f;
		g_TexCoord = (d_TexCoord + ex_TexCoord[1] + ex_TexCoord[2]) / 3.f;
		g_Tangent = (d_Tangent + ex_Tangent[1] + ex_Tangent[2]) / 3.f;
		g_Bitangent = (d_Bitangent + ex_Bitangent[1] + ex_Bitangent[2]) / 3.f;
		g_tbnView = (d_tbnView + ex_tbnView[1] + ex_tbnView[2]) / 3.f;

		vec2 g_coords = tex_coords(height_map,g_TexCoord);
		float g_height = texture(height_map.tex, g_coords).x;
		PositionG += h_mult * g_height * g_Normal;
	
		/* Vertex A */
		gl_Position = in_Projection * vec4(PositionA,1.f);
		Position   = PositionA;
		Normal     = ex_Normal[0];
		TexCoord   = ex_TexCoord[0];
		Tangent    = ex_Tangent[0];
		Bitangent  = ex_Bitangent[0];
		tbnView    = ex_tbnView[0];
		EmitVertex();

		/* Vertex B */
		gl_Position = in_Projection * vec4(PositionB,1.f);
		Position   = PositionB;
		Normal     = ex_Normal[1];
		TexCoord   = ex_TexCoord[1];
		Tangent    = ex_Tangent[1];
		Bitangent  = ex_Bitangent[1];
		tbnView    = ex_tbnView[1];
		EmitVertex();

		/* Vertex E */
		gl_Position = in_Projection * vec4(PositionE,1.f);
		Position = PositionE;
		Normal = e_Normal;
		TexCoord = e_TexCoord;
		Tangent = e_Tangent;
		Bitangent = e_Bitangent;
		tbnView = e_tbnView;
		EmitVertex();

		/* Vertex D */
		gl_Position = in_Projection * vec4(PositionD,1.f);
		Position = PositionD;
		Normal = d_Normal;
		TexCoord = d_TexCoord;
		Tangent = d_Tangent;
		Bitangent = d_Bitangent;
		tbnView = d_tbnView;
		EmitVertex();

		/* Vertex A */
		gl_Position = in_Projection * vec4(PositionA,1.f);
		Position   = PositionA;
		Normal     = ex_Normal[0];
		TexCoord   = ex_TexCoord[0];
		Tangent    = ex_Tangent[0];
		Bitangent  = ex_Bitangent[0];
		tbnView    = ex_tbnView[0];
		EmitVertex();

		/* Vertex F */
		gl_Position = in_Projection * vec4(PositionF,1.f);
		Position = PositionF;
		Normal = f_Normal;
		TexCoord = f_TexCoord;
		Tangent = f_Tangent;
		Bitangent = f_Bitangent;
		tbnView = f_tbnView;
		EmitVertex();

		/* Vertex C */
		gl_Position = in_Projection * vec4(PositionC,1.f);
		Position   = PositionC;
		Normal     = ex_Normal[2];
		TexCoord   = ex_TexCoord[2];
		Tangent    = ex_Tangent[2];
		Bitangent  = ex_Bitangent[2];
		tbnView    = ex_tbnView[2];
		EmitVertex();

		/* Vertex D */
		gl_Position = in_Projection * vec4(PositionD,1.f);
		Position = PositionD;
		Normal = d_Normal;
		TexCoord = d_TexCoord;
		Tangent = d_Tangent;
		Bitangent = d_Bitangent;
		tbnView = d_tbnView;
		EmitVertex();

		/* Vertex G */
		gl_Position = in_Projection * vec4(PositionG,1.f);
		Position = PositionG;
		Normal = g_Normal;
		TexCoord = g_TexCoord;
		Tangent = g_Tangent;
		Bitangent = g_Bitangent;
		tbnView = g_tbnView;
		EmitVertex();

		/* Vertex B */
		gl_Position = in_Projection * vec4(PositionB,1.f);
		Position   = PositionB;
		Normal     = ex_Normal[1];
		TexCoord   = ex_TexCoord[1];
		Tangent    = ex_Tangent[1];
		Bitangent  = ex_Bitangent[1];
		tbnView    = ex_tbnView[1];
		EmitVertex();

		/* Vertex C */
		gl_Position = in_Projection * vec4(PositionC,1.f);
		Position   = PositionC;
		Normal     = ex_Normal[2];
		TexCoord   = ex_TexCoord[2];
		Tangent    = ex_Tangent[2];
		Bitangent  = ex_Bitangent[2];
		tbnView    = ex_tbnView[2];
		EmitVertex();

		EndPrimitive();

	}

		
}
