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
 * 
 * ## Points
 *
 * - A: Left Camera
 * - B: Right Camera
 * - C: Marker
 */
export function calculateCoordinates(leftCameraAngles: Angles, rightCameraAngles: Angles) {
    const absAC = calculateDistanceToC(leftCameraAngles.horizontalAngleRad, rightCameraAngles.horizontalAngleRad);
    const absBC = calculateDistanceToC(rightCameraAngles.horizontalAngleRad, leftCameraAngles.horizontalAngleRad);

    const x_per_absAC = (Math.pow(absAC, 2) + Math.pow(DISTANCE_BETWEEN_CAMERAS_m, 2) - Math.pow(absBC, 2)) / (2 * absAC * DISTANCE_BETWEEN_CAMERAS_m);
    const x = absAC * x_per_absAC;
    const r = absAC * Math.sin(Math.acos(x_per_absAC));
    const y = Math.cos(leftCameraAngles.verticalAngleRad) * r;
    const z = Math.sin(leftCameraAngles.verticalAngleRad) * r;

    return {
        x: roundPrecision(x),
        y: roundPrecision(y),
        z: roundPrecision(z)
    };
}

/**
 * ## Points
 *
 * - A: Left Camera
 * - B: Right Camera
 * - C: Marker
 *
 * ## Sketch
 * 
 * ```
 *           C_
 *          /  °__
 *     b1  /      °__
 *        /          °__
 *       /              °__
 *      /°_____            °__
 * b2  /       °_____  d      °__
 *    /              °_____      °__
 *   /                     °_____   °__
 *  /                           °_____ °__
 * A°^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^°B
 * ```
 */
export function calculateDistanceToC(alpha: number, beta: number) {
    const c = DISTANCE_BETWEEN_CAMERAS_m;

    const d = Math.sin(alpha) * c;
    const b1 = Math.cos(alpha) * c;
    const gamma = Math.PI - alpha - beta;
    if (alpha + beta > (1 / 2) * Math.PI) {
        const b2 = d / Math.tan(gamma);
        return b1 + b2;
    } else if (alpha + beta < (1 / 2) * Math.PI) {
        const b2 = d / Math.tan(Math.PI - gamma);
        return b1 - b2;
    } else {
        return b1;
    }
}
