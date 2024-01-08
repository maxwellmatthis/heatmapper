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
