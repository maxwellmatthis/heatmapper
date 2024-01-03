# location-service

The location service calculates the location of the marker based on angle measurements from two smartphone cameras. The coordinate system origin `(0, 0, 0)^T` is located at the left camera. The right camera must be set up `1m` to the right of the left camera at `(1, 0, 0)^T`. The configuration can be modified by changing the `DISTANCE_BETWEEN_CAMERAS_m` constant in `trig.ts`.

## Installation

__Prerequisites__:

- [Bun](https://bun.sh)

1. Install dependencies: `bun install`

## Usage

1. Set `HM_KEY` environment variable to a key phrase. This will be required to connect to the server.
2. Set the `BUN_PORT` environment variable to a port of your choosing. Defaults to `3000`.
3. Run the server using `bun run .`.
4. Navigate to the server's hostname and port in your browser.

## Tests

Tests can be run using `bun test`.

## Sources

The specific knowledge required to write this service came from the following pieces of documentation.

- [Bun HTTP Server](https://bun.sh/docs/api/http)
- [Bun WebSockets](https://bun.sh/docs/api/websockets)
- [MDN - ImageData](https://developer.mozilla.org/en-US/docs/Web/API/ImageData/data)
- [MDN - Media Capture and Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Media_Capture_and_Streams_API/Taking_still_photos)
