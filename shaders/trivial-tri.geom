// Geometry Shader – file "trivial-tri.geom"
#version 330

/* uniform mat4 in_Modelview; */
/* uniform mat4 in_Projection; */

/* in  vec3 in_Position; */
/* in  vec3 in_Normal; */
/* in  vec2 in_TexCoord; */

/* smooth out vec3 ex_Position; */
/* smooth out vec3 ex_Normal; */
/* smooth out vec3 ex_Color; */
/* smooth out vec2 ex_TexCoord; */
/* out float light_inc; */

/* out vec3 light_source; */

/* precision highp float; */

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;


void main(void)
{
	for (int i = 0; i < 3; ++i) {
		gl_Position = gl_in[i].gl_Position;
		EmitVertex();
	}
	EndPrimitive();
}
