// Taken from:
// https://github.com/PRBonn/overlap_localization/blob/master/src/prepare_training/c_utils/src/c_gen_depth_and_normal.cpp
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

int wrap(int x, int dim) {
    int value = x;
    if (value >= dim) {
        value = value - dim;
    }
    if (value < 0) {
        value = value + dim;
    }
    return value;
}

py::array_t<float> gen_normal_map(const py::array_t<float> &range,
                                  const py::array_t<float> &vertex,
                                  const int W,
                                  const int H) {
    pybind11::buffer_info buf1 = range.request();
    pybind11::buffer_info buf2 = vertex.request();

    /*  allocate the buffer */
    py::array_t<float> normal_map_buffer = py::array_t<float>(buf2.size);

    pybind11::buffer_info buf3 = normal_map_buffer.request();

    auto *depth_buffer = (float *)buf1.ptr;
    auto *vertex_map = (float *)buf2.ptr;
    auto *normal_map = (float *)buf3.ptr;

#pragma omp parallel for
    for (int i = 0; i < H * W * 3; ++i) {
        normal_map[i] = 0;
    }

#pragma omp parallel
    {
#pragma omp for nowait collapse(2)
        for (int x = 0; x < W; ++x) {
            for (int y = 0; y < H - 1; ++y) {
                const float &px = vertex_map[y * W * 3 + x * 3];
                const float &py = vertex_map[y * W * 3 + x * 3 + 1];
                const float &pz = vertex_map[y * W * 3 + x * 3 + 2];
                const float &depth = depth_buffer[y * W + x];

                if (depth > 0) {
                    int wrap_x = wrap(x + 1, W);
                    const float &ux = vertex_map[y * W * 3 + wrap_x * 3];
                    const float &uy = vertex_map[y * W * 3 + wrap_x * 3 + 1];
                    const float &uz = vertex_map[y * W * 3 + wrap_x * 3 + 2];
                    const float &u_depth = depth_buffer[y * W + wrap_x];
                    if (u_depth <= 0) {
                        continue;
                    }

                    const float &vx = vertex_map[(y + 1) * W * 3 + x * 3];
                    const float &vy = vertex_map[(y + 1) * W * 3 + x * 3 + 1];
                    const float &vz = vertex_map[(y + 1) * W * 3 + x * 3 + 2];
                    const float &v_depth = depth_buffer[(y + 1) * W + x];
                    if (v_depth <= 0) {
                        continue;
                    }

                    float l = 0.0;
                    float u_normx = ux - px;
                    float u_normy = uy - py;
                    float u_normz = uz - pz;
                    l = sqrt(u_normx * u_normx + u_normy * u_normy +
                             u_normz * u_normz);
                    u_normx /= l;
                    u_normy /= l;
                    u_normz /= l;

                    float v_normx = vx - px;
                    float v_normy = vy - py;
                    float v_normz = vz - pz;
                    l = sqrt(v_normx * v_normx + v_normy * v_normy +
                             v_normz * v_normz);
                    v_normx /= l;
                    v_normy /= l;
                    v_normz /= l;

                    const float crossx = u_normz * v_normy - u_normy * v_normz;
                    const float crossy = u_normx * v_normz - u_normz * v_normx;
                    const float crossz = u_normy * v_normx - u_normx * v_normy;
                    float norm = sqrt(crossx * crossx + crossy * crossy +
                                      crossz * crossz);

#pragma omp critical
                    if (norm > 0) {
                        const float normalx = crossx / norm;
                        const float normaly = crossy / norm;
                        const float normalz = crossz / norm;
                        normal_map[y * W * 3 + x * 3] = normalx;
                        normal_map[y * W * 3 + x * 3 + 1] = normaly;
                        normal_map[y * W * 3 + x * 3 + 2] = normalz;
                    }
                }
            }
        }
    }

    // reshape array to match input shape
    normal_map_buffer.resize({H, W, 3});
    return normal_map_buffer;
}

PYBIND11_MODULE(normal_map, m) {
    m.doc() = "generate normal map using pybind11";
    m.def("gen_normal_map", &gen_normal_map, "generate normal map");
}
