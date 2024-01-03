import type { Server } from "bun";
import { join } from "path";
import { type Angles, calculateCoordinates, VERTICAL_ANGLE_DIFFERENCE_TOLERANCE_rad } from "./trig";

const HM_KEY_ENV = "HM_KEY";
const EXCHANGE_CHANNEL = "exchange";

if (typeof Bun.env[HM_KEY_ENV] === "undefined") {
    console.error(`Please set the "${HM_KEY_ENV}" environment variable to a key phrase.`);
    process.exit(2);
};

enum Role {
    leftCamera = "leftCamera",
    rightCamera = "rightCamera",
}

const server = Bun.serve<{ role: Role; }>({
    development: false,
    async fetch(req, server) {
        const url = new URL(req.url);

        // public
        if (url.pathname === "/") return new Response(Bun.file(join("static", "index.html")));
        if (url.pathname === "/camera") return new Response(Bun.file(join("static", "camera.html")));
        if (url.pathname === "/camera.js") return new Response(Bun.file(join("static", "camera.js")));

        // authorized
        if (["/exchange", "/location"].includes(url.pathname)) {
            if (url.searchParams.get("key") !== Bun.env[HM_KEY_ENV]) {
                return new Response(
                    "Error 401: Unauthorized." +
                    "\nYour access was denied because you provided an invalid key or no key.",
                    { status: 401 }
                );
            }

            if (url.pathname === "/exchange") return Exchange(req, server, url);
            if (url.pathname === "/location") return await Location(server);
        }

        return new Response("Error 404: Not Found.", { status: 404 });
    },
    websocket: {
        open: (ws) => { ws.subscribe(EXCHANGE_CHANNEL); },
        message: (ws, message) => {
            handleAnglesMessage(message, ws.data.role);
        },
        close: (ws) => { ws.unsubscribe(EXCHANGE_CHANNEL); },
    },
});

console.log(`Listening on ${server.hostname}:${server.port}`);


function Exchange(req: Request, server: Server, url: URL) {
    let role = url.searchParams.get("camera");
    if (role !== Role.leftCamera && role !== Role.rightCamera) {
        return new Response(
            `Error: Invalid role. Must be "${Role.leftCamera}" or "${Role.rightCamera}".`,
            { status: 400 }
        );
    }

    const upgraded = server.upgrade(req, { data: { role } });
    if (!upgraded) {
        return new Response("WebSocket upgrade error", { status: 400 });
    }
}

type AngleResolver = ((angles: Angles) => void) | null;
let resolveLeftCamera: AngleResolver = null;
let resolveRightCamera: AngleResolver = null;

type AngleRejecter = ((reason: string) => void) | null;
let rejectLeftCamera: AngleRejecter = null;
let rejectRightCamera: AngleRejecter = null;

const clearCameraCallbacks = () => {
    resolveLeftCamera = null;
    resolveRightCamera = null;
    rejectLeftCamera = null;
    rejectRightCamera = null;
};

async function Location(server: Server) {
    const cameraPromises = Promise.all([
        new Promise<Angles>((resolve, reject) => {
            resolveLeftCamera = resolve;
            rejectLeftCamera = reject;
        }),
        new Promise<Angles>((resolve, reject) => {
            resolveRightCamera = resolve;
            rejectRightCamera = reject;
        })
    ]);
    server.publish(EXCHANGE_CHANNEL, "find-marker");

    try {
        const [leftCameraAngles, rightCameraAngles] = await cameraPromises;
        clearCameraCallbacks();

        const absVerticalAngleDifferenceRad = Math.abs(leftCameraAngles.verticalAngleRad - rightCameraAngles.verticalAngleRad);
        // if (absVerticalAngleDifferenceRad > VERTICAL_ANGLE_DIFFERENCE_TOLERANCE_rad) {
        //     console.warn(
        //         `WARNING: The vertical angles differ by ${absVerticalAngleDifferenceRad / (Math.PI / 180)}`
        //         + `°. These angles should ideally be the same. The difference tolerance is set to `
        //         + `${VERTICAL_ANGLE_DIFFERENCE_TOLERANCE_rad / (Math.PI / 180)}°.`);
        // }
        const { x, y, z } = calculateCoordinates(leftCameraAngles, rightCameraAngles);
        return new Response(JSON.stringify({
            x,
            y,
            z,
            absVerticalAngleDifferenceRad,
            VERTICAL_ANGLE_DIFFERENCE_TOLERANCE_rad,
            leftCameraAngles,
            rightCameraAngles
        }, null, 2));
    } catch (error) {
        clearCameraCallbacks();
        return new Response(String(error));
    }
}

function handleAnglesMessage(message: string | Buffer, role: Role) {
    try {
        const parsed: Angles = JSON.parse(String(message));
        if (typeof parsed.horizontalAngleRad !== "number" || typeof parsed.verticalAngleRad !== "number") {
            throw new Error(`Invalid Angles Object: ${message}`);
        }

        if (role === Role.leftCamera) resolveLeftCamera && resolveLeftCamera(parsed);
        else if (role === Role.rightCamera) resolveRightCamera && resolveRightCamera(parsed);
    } catch (error) {
        // DEBUG
        console.error(error);
        if (role === Role.leftCamera) rejectLeftCamera && rejectLeftCamera("Result from left camera was invalid.");
        else if (role === Role.rightCamera) rejectRightCamera && rejectRightCamera("Result from right camera was invalid.");
    }
}
