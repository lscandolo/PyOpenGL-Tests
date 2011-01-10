#version 330
out vec4 fragColor;
uniform samplerCube cubemap;
varying vec3 ex_texcoord;
void main(void){fragColor = texture(cubemap, ex_texcoord);}
