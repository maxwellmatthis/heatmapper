import { expect, test } from "bun:test";
import { calculateCoordinates, roundTo } from "./trig";

// -- rounding --
test("pi (3.1415926536) to 5 decimals precision", () => {
  expect(roundTo(3.1415926536))
    .toBe(3.14159);
});

test("e (2.7182818285) to 2 decimals precision", () => {
  expect(roundTo(2.7182818285, 2))
    .toBe(2.72);
});

// -- horizontal --
test("both 60° horizontal", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (1 / 3) * Math.PI,
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: (1 / 3) * Math.PI,
    verticalAngleRad: 0
  })).toEqual({
    x: 0.5,
    y: 0.86603,
    z: 0
  });
});

test("both 30° horizontal", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (1 / 6) * Math.PI,
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: (1 / 6) * Math.PI,
    verticalAngleRad: 0
  })).toEqual({
    // TODO: calculate real
    x: 0.5,
    y: 0.0,
    z: 0
  });
});

test("one meter in front of left camera", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (1 / 2) * Math.PI,
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: Math.atan(1 / 1),
    verticalAngleRad: 0
  })).toEqual({
    x: 0,
    y: 1,
    z: 0
  });
});

// -- horizontal and vertical --
test("both 60° horizontal and 45° vertical", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (1 / 3) * Math.PI,
    verticalAngleRad: (1 / 4) * Math.PI
  }, {
    horizontalAngleRad: (1 / 3) * Math.PI,
    verticalAngleRad: (1 / 4) * Math.PI
  })).toEqual({
    // TODO: calculate real
    x: 0.5,
    y: 0.5,
    z: 0.5
  });
});
