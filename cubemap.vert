#version 330
in vec4 in_pos;
uniform mat4 mvpTransf;
varying vec3 ex_texcoord;
void main(void){
  ex_texcoord = normalize(in_pos.xyz);
  gl_Position = mvpTransf * in_pos;
}
