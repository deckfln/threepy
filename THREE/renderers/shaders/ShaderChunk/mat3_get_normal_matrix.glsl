/*
mat3 mat3_get_normal_matrix(const mat4 matrix4)
{
    mat3 self;

    self[0][0] = matrix4[0][0];    self[1][0] = matrix4[1][0];    self[2][0] = matrix4[2][0];
    self[0][1] = matrix4[0][1];    self[1][1] = matrix4[1][1];    self[2][1] = matrix4[2][1];
    self[0][2] = matrix4[0][2];    self[1][2] = matrix4[1][2];    self[2][2] = matrix4[2][2];

    self = inverse(self);
    self = transpose(self);

    return self;
}
*/