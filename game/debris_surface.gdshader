shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
// Same BoxMesh, same depth/shadow passes, no displacement or extra draw call.
// Dark face borders keep adjoining amber faces from merging into a bright ribbon.
uniform vec4 tint : source_color = vec4(1.0);
uniform bool instance_colors = false;
varying vec3 local_position;
void vertex() {
    local_position = VERTEX / 0.17;
}
void fragment() {
    vec3 a = abs(local_position);
    float second = max(min(a.x, a.y), min(max(a.x, a.y), a.z));
    float aa = max(fwidth(second), 0.015);
    float edge = smoothstep(0.82 - aa, 0.82 + aa, second);
    vec3 base = instance_colors ? COLOR.rgb : tint.rgb;
    ALBEDO = mix(base, base * 0.24, edge);
    ROUGHNESS = 0.86;
}
