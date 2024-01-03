export interface Angles {
    horizontalAngleRad: number;
    verticalAngleRad: number;
}

export const DISTANCE_BETWEEN_CAMERAS_m = 1;
/** 120° in radians. (two angles of an equilateral triangle) */
const DEG_120_RAD = (2 / 3) * Math.PI;

export function roundTo(n: number, decimals: number = 5) {
    const decimalsMover = Math.pow(10, decimals);
    return Math.round(n * decimalsMover) / decimalsMover;
}

export function calculateCoordinates(leftCameraAngles: Angles, rightCameraAngles: Angles) {
    // -- horizontal part --
    //                    C: Marker
    //                    /\
    //             h_b   /  \  h_a
    //                  /    \
    //                 /      \
    // A: Left Camera /________\ B: Right Camera
    //                   h_c = DISTANCE_BETWEEN_CAMERAS_m

    const h_alpha = leftCameraAngles.horizontalAngleRad;
    const h_beta = rightCameraAngles.horizontalAngleRad;
    const h_c = DISTANCE_BETWEEN_CAMERAS_m;
    let h_b: number | null = null;

    if (h_alpha === h_beta) {
        if (h_alpha + h_beta === DEG_120_RAD) {
            // hypotenuse: `h_c`, `h_a` and `h_b`
            h_b = h_c;
        } else if (h_alpha + h_beta < DEG_120_RAD) {
            // hypotenuse: `h_c`
            // `sin(h_beta) = h_b / h_c`
            h_b = Math.sin(h_beta) * h_c;
        } else {
            // hypotenuse: `h_b` and `h_a`
            // `cos(h_alpha) = (h_c / 2) / h_b`
            h_b = (h_c / 2) / Math.cos(h_alpha);
        }
    } else {
        if (h_alpha + h_beta < DEG_120_RAD) {
            // hypotenuse: `h_c`
            // `sin(h_beta) = h_b / h_c`
            h_b = Math.sin(h_beta) * h_c;
        } else {
            if (h_alpha > h_beta) {
                // hypotenuse: `h_a`
                // `cos(h_beta) = h_c / h_a`
                let h_a = h_c / Math.cos(h_beta);
                // Using: Law of Cosines (`c^2 = a^2 + b^2 - 2ab*cos(gamma)`)
                h_b = Math.sqrt(Math.pow(h_a, 2) + Math.pow(h_c, 2) - 2 * h_a * h_c * Math.cos(h_beta));
            } else {
                // hypotenuse: `h_b`
                // `cos(h_alpha) = h_c / h_b`
                h_b = h_c / Math.cos(h_alpha);
            }
        }
    }

    // const h_C_x = Math.cos(h_alpha) * h_b;
    // const h_C_y = Math.sin(h_alpha) * h_b;
    // console.log(v_C_x, v_C_y);

    // -- vertical part --
    //                    *
    //                       *     v_a: Elevation
    //                        _*  /
    //                    __° | */
    //           h_b  __°     | /*
    //            __°         |L  *
    //        __°    \        |    *
    //    __° v_alpha \     /.|    *
    // (A)-------------------------*
    //     h_b: Distance to Marker *
    //    |<----------------->|    *
    //     h_r: Real Horizontal   *
    //                           *
    //                          *
    //                        *

    const v_alpha = leftCameraAngles.verticalAngleRad;

    const v_a = Math.sin(v_alpha) * h_b;
    const h_r = Math.cos(v_alpha) * h_b;

    const C_x = Math.cos(h_alpha) * h_r;
    const C_y = Math.sin(h_alpha) * h_r;
    const C_z = v_a;

    return { x: roundTo(C_x), y: roundTo(C_y), z: roundTo(C_z) };
}
