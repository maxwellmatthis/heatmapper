// -- Settings --
const cameraProfile = document.querySelector("select#cameraProfile");
const cameraId = document.querySelector("select#cameraId");
const markerType = document.querySelector("select#markerType");

function degToRad(degrees) {
    return degrees * (Math.PI / 180);
}

const cameraProfileDefinitions = {
    "desktop": {
        horizontalViewFieldRad: degToRad(60),
        verticalViewFieldRad: degToRad(18),
    }
};

const markerTypeCheckDefinitions = {
    /**
     * @param {number[]} brightest 
     * @param {number[]} current 
     */
    "brightest": (brightest, current) => {
        const [R, G, B, A] = brightest;
        const [r, g, b, a] = current;

        return (
            r >= R &&
            g >= G &&
            b >= B &&
            a >= A
        );
    },
    /**
     * @param {number[]} mostRed 
     * @param {number[]} current 
     */
    "mostRed": (mostRed, current) => {
        const [R, G, B, A] = mostRed;
        const [r, g, b, a] = current;

        return (
            r >= R &&
            g <= 255 / 2 &&
            b <= 255 / 2 &&
            a >= A
        );
    },
    /**
     * @param {number[]} mostGreen 
     * @param {number[]} current 
     */
    "mostGreen": (mostGreen, current) => {
        const [R, G, B, A] = mostGreen;
        const [r, g, b, a] = current;

        return (
            r <= R &&
            g >= G &&
            b <= B &&
            a >= A
        );
    },
    /**
     * @param {number[]} mostBlue 
     * @param {number[]} current 
     */
    "mostBlue": (mostBlue, current) => {
        const [R, G, B, A] = mostBlue;
        const [r, g, b, a] = current;

        return (
            r <= R &&
            g <= G &&
            b >= B &&
            a >= A
        );
    },
};

// -- Preview and Image Processing --
const video = document.querySelector("video#previewStream");
const canvas = document.querySelector("canvas#previewTrackingResult");
const ctx = canvas.getContext("2d");
const trackingResultX = document.querySelector("span#previewTrackingResultX");
const trackingResultY = document.querySelector("span#previewTrackingResultY");
const trackingResultHorizontal = document.querySelector("span#previewTrackingResultHorizontal");
const trackingResultVertical = document.querySelector("span#previewTrackingResultVertical");
const findMarkerNow = document.querySelector("button#findMarkerNow");

const hiddenCanvas = document.createElement("canvas");
const hiddenCtx = hiddenCanvas.getContext("2d");

if (!window?.navigator?.mediaDevices?.getUserMedia) {
    document.querySelector("div#streamWarning").style.display = "";
    if (!window.location.protocol.includes("s")) document.querySelector("p#streamWarningInsecureContext").style.display = "";
    alert("`window?.navigator?.mediaDevices?.getUserMedia` does not exist.");
} else {
    navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
            video.srcObject = stream;
            video.play();
        })
        .catch((err) => {
            console.error(err);
        });
}

const width = document.body.clientWidth;
let height = 0;
let streaming = false;
video.addEventListener(
    "canplay",
    (ev) => {
        if (streaming) return;

        height = video.videoHeight / (video.videoWidth / width);

        // Firefox currently has a bug where the height can't be read from
        // the video, so we will make assumptions if this happens.

        if (isNaN(height)) {
            height = width / (4 / 3);
        }

        video.setAttribute("width", width);
        video.setAttribute("height", height);
        canvas.setAttribute("width", width);
        canvas.setAttribute("height", height);
        hiddenCanvas.setAttribute("width", video.videoWidth);
        hiddenCanvas.setAttribute("height", video.videoHeight);
        streaming = true;
    },
    false
);


/**
 * @param {number} x 
 * @param {number} y 
 */
const calculateAnglesTo = (x, y) => {
    const cpd = cameraProfileDefinitions[cameraProfile.value];

    let horizontalSidedAngleRad;
    if (cameraId.value === "leftCamera") horizontalSidedAngleRad = cpd.horizontalViewFieldRad - ((x / video.videoWidth) * cpd.horizontalViewFieldRad); // angle from right
    else if (cameraId.value === "rightCamera") horizontalSidedAngleRad = ((x / video.videoWidth) * cpd.horizontalViewFieldRad); // angle from left
    else throw new Error("Bad Programmer");

    const oneSideHorizontalBlindSpotRad = (Math.PI - cpd.horizontalViewFieldRad) / 2;

    return {
        horizontalAngleRad:
            horizontalSidedAngleRad
            + oneSideHorizontalBlindSpotRad,
        verticalAngleRad:
            ((y / video.videoHeight) * cpd.verticalViewFieldRad) // angle from top
            - (cpd.verticalViewFieldRad / 2) // normalize so that 0° is the center
            * -1 // flip so that +30°, for example, is up from center
    };
};

/**
 * @type {() => { x: number, y: number, horizontalAngleRad: number, verticalAngleRad: number; }}
 */
const findMarker = () => {
    hiddenCtx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    const imageData = hiddenCtx.getImageData(0, 0, video.videoWidth, video.videoHeight);

    const VALUES_PER_PIXEL = 4;
    const VALUES_PER_ROW = video.videoWidth * VALUES_PER_PIXEL;
    let best = [0, 0, 0, 0];
    let best_x = 0;
    let best_y = 0;

    let pixel_base = 0;
    for (pixel_base = 0; pixel_base < imageData.data.length; pixel_base += VALUES_PER_PIXEL) {
        const currentRgba = [
            imageData.data[pixel_base + 0],
            imageData.data[pixel_base + 1],
            imageData.data[pixel_base + 2],
            imageData.data[pixel_base + 3]
        ];

        if (markerTypeCheckDefinitions[markerType.value](best, currentRgba)) {
            best = currentRgba;
            best_x = (pixel_base % VALUES_PER_ROW) / 4;
            best_y = (pixel_base - best_x * 4) / VALUES_PER_ROW;
        }
    }

    // easier to see blue circle around marker
    hiddenCtx.beginPath();
    hiddenCtx.strokeStyle = "#02c8ff";
    hiddenCtx.lineWidth = 4;
    hiddenCtx.arc(best_x, best_y, 32, 0, 2 * Math.PI);
    hiddenCtx.stroke();
    // more exact red circle around marker
    hiddenCtx.beginPath();
    hiddenCtx.strokeStyle = "#ff0000";
    hiddenCtx.lineWidth = 1;
    hiddenCtx.arc(best_x, best_y, 3, 0, 2 * Math.PI);
    hiddenCtx.stroke();

    ctx.drawImage(hiddenCanvas, 0, 0, width, height);

    const { horizontalAngleRad, verticalAngleRad } = calculateAnglesTo(best_x, best_y);
    trackingResultX.textContent = best_x;
    trackingResultY.textContent = best_y;
    trackingResultHorizontal.textContent = Math.floor((horizontalAngleRad / (Math.PI / 180)) * 100) / 100 + "°";
    trackingResultVertical.textContent = Math.floor((verticalAngleRad / (Math.PI / 180)) * 100) / 100 + "°";

    return { x: best_x, y: best_y, horizontalAngleRad, verticalAngleRad };
};

findMarkerNow.addEventListener("click", findMarker);

// -- Connect --
const key = document.querySelector("input#key");
const connect = document.querySelector("button#connect");
const connectionStatus = document.querySelector("span#connectionStatus");

// restore from local storage
const HM_KEY = "hm_key";
const savedKey = window.localStorage.getItem(HM_KEY);
if (savedKey) key.value = savedKey;
const HM_CAMERA_ID = "hm_camera_id";
const savedCameraId = window.localStorage.getItem(HM_CAMERA_ID);
if (savedCameraId) cameraId.value = savedCameraId;

let websocket = null;

connect.addEventListener("click", () => {
    if (!key.value) {
        alert("Please provide a key.");
        return;
    }

    window.localStorage.setItem(HM_KEY, key.value);
    window.localStorage.setItem(HM_CAMERA_ID, cameraId.value);

    if (websocket) {
        websocket.close();
    }

    websocket = new WebSocket(`/exchange?key=${key.value}&camera=${cameraId.value}`);
    websocket.addEventListener("open", () => {
        connectionStatus.textContent = "Connected ✅";
        websocket.addEventListener("message", (ev) => {
            if (ev.data === "find-marker") {
                const { horizontalAngleRad, verticalAngleRad } = findMarker();
                websocket.send(JSON.stringify({ horizontalAngleRad, verticalAngleRad }));
            }
        });
    });
    websocket.addEventListener("close", () => {
        connectionStatus.textContent = "Disconnected ❌";
    });
});
