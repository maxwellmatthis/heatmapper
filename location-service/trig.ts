export interface Angles {
    horizontalAngleRad: number;
    verticalAngleRad: number;
}

export const DISTANCE_BETWEEN_CAMERAS_m = 1;
export const VERTICAL_ANGLE_DIFFERENCE_TOLERANCE_rad = (5 / 180) * Math.PI;

export function roundPrecision(n: number, decimals: number = 5) {
    const decimalsMover = Math.pow(10, decimals);
    return Math.round(n * decimalsMover) / decimalsMover;
}

/**
 * Calculates the three dimensional coordinates of an object based on the angles to the object
 * from two points.
 * 
 * @param leftCameraAngles The angle data from the left camera.
 * @param rightCameraAngles The angle data from the right camera.
 * @param distanceBetweenCameras The distance between the cameras. This parameter may be used as an override for the default value `DISTANCE_BETWEEN_CAMERAS_m`.
 * 
 * ## Points
 *
 * - A: Left Camera
 * - B: Right Camera
 * - C: Marker
 */
export function calculateCoordinates(leftCameraAngles: Angles, rightCameraAngles: Angles, distanceBetweenCameras = DISTANCE_BETWEEN_CAMERAS_m) {
    const absAC = calculateLengthAC(leftCameraAngles.horizontalAngleRad, rightCameraAngles.horizontalAngleRad, distanceBetweenCameras);

    const x = absAC * Math.cos(leftCameraAngles.horizontalAngleRad);
    const r = absAC * Math.sin(leftCameraAngles.horizontalAngleRad);
    const y = r * Math.cos(leftCameraAngles.verticalAngleRad);
    const z = r * Math.sin(leftCameraAngles.verticalAngleRad);

    return {
        x: roundPrecision(x),
        y: roundPrecision(y),
        z: roundPrecision(z)
    };
}

/**
 * Calculates the length of `AC` given the angles `alpha` and `beta`.
 * 
 * @param alpha The angle alpha (see sketch).
 * @param beta The angle beta (see sketch).
 * @param distanceBetweenCameras The distance between the cameras. This parameter may be used as an override for the default value `DISTANCE_BETWEEN_CAMERAS_m`.
 * 
 * ## Points
 *
 * - A: Left Camera
 * - B: Right Camera
 * - C: Marker
 *
 * ## Sketch
 * 
 * - only alpha, beta and c are known
 * - d ⏊ b
 * 
 * ```
 * >            C_
 * >           /  °,_
 * >          /      °,_
 * >         / b1       °,_
 * >        /              °,_  a
 * >     b /°--,__            °,_
 * >      /       °--,__  d      °,_
 * >     / b2           °--,__      °,_
 * >    /                     °--,__   °,_
 * >   /                            °--,__°,_
 * >  A°^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^°B
 * >                     c = DISTANCE_BETWEEN_CAMERAS_m
 * ```
 */
export function calculateLengthAC(alpha: number, beta: number, distanceBetweenCameras = DISTANCE_BETWEEN_CAMERAS_m) {
    const c = distanceBetweenCameras;

    // sin(alpha) = d / c
    const d = Math.sin(alpha) * c;
    // cos(alpha) = b1 / c
    const b1 = Math.cos(alpha) * c;
    // 180° = alpha + beta + gamma
    const gamma = Math.PI - alpha - beta;

    if (alpha + beta > (1 / 2) * Math.PI) {
        // gamma is acute
        // tan(gamma) = d / b2
        const b2 = d / Math.tan(gamma);
        return b1 + b2;
    } else if (alpha + beta < (1 / 2) * Math.PI) {
        // gamma is obtuse
        // tan(pi - gamma) = d / b2
        const b2 = d / Math.tan(Math.PI - gamma);
        return b1 - b2;
    } else {
        // gamma is right
        return b1;
    }
}
