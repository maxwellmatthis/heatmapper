import { expect, test } from "bun:test";
import { calculateLengthAC, calculateCoordinates, roundPrecision } from "./trig";

// -- rounding --
test("pi (3.1415926536) to 5 decimals precision", () => {
  expect(roundPrecision(3.1415926536))
    .toBe(3.14159);
});

test("e (2.7182818285) to 2 decimals precision", () => {
  expect(roundPrecision(2.7182818285, 2))
    .toBe(2.72);
});

// -- distance to C --
test("both 60° horizontal", () => {
  expect(calculateLengthAC(
    (1 / 3) * Math.PI,
    (1 / 3) * Math.PI
  ))
    .toBeCloseTo(1, 5);
});

test("left 45°, right 60°", () => {
  expect(calculateLengthAC(
    (1 / 4) * Math.PI,
    (1 / 3) * Math.PI
  ))
    .toBeCloseTo(0.8965754721680536, 5);
});

test("left 1°, right 178°", () => {
  expect(calculateLengthAC(
    (1 / 180) * Math.PI,
    (178 / 180) * Math.PI
  ))
    .toBeCloseTo(1.9996953903127683, 5);
});

test("switching the order of the parameters to get the other distance", () => {
  expect(calculateLengthAC(
    (1 / 180) * Math.PI,
    (178 / 180) * Math.PI
  ) + calculateLengthAC(
    (178 / 180) * Math.PI,
    (1 / 180) * Math.PI
  ))
    .toBeCloseTo(3);
});

// -- coordinates --
test("2m in front of left camera", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (1 / 2) * Math.PI,
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: Math.atan(2 / 1),
    verticalAngleRad: 0
  }))
    .toEqual({
      x: 0,
      y: 2,
      z: 0
    });
});

test("4m in front of right camera", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: Math.atan(4 / 1),
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: (1 / 2) * Math.PI,
    verticalAngleRad: 0
  }))
    .toEqual({
      x: 1,
      y: 4,
      z: 0
    });
});

test("horizontal angles 60° and 45°, vertical 0°", () => {
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: (1 / 3) * Math.PI,
    verticalAngleRad: 0
  }, {
    horizontalAngleRad: (1 / 4) * Math.PI,
    verticalAngleRad: 0
  });
  expect(x).toBeCloseTo(0.36603, 5);
  expect(y).toBeCloseTo(0.63397, 5);
  expect(z).toBeCloseTo(0, 5);
});

test("all angles 60°", () => {
  const ANGLE = (1 / 3) * Math.PI;
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  }, {
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  });
  expect(x).toBeCloseTo(0.5, 5);
  expect(y).toBeCloseTo(0.43301, 5);
  expect(z).toBeCloseTo(0.75, 5);
});

test("60° vertical, 10m between cameras, same y-coordinate as other 60° test, half distance x-coordinate", () => {
  const DISTANCE = 100;
  const ANGLE = (1 / 3) * Math.PI;
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: 0.01731877634, // value calculated using a calculator and piece of paper
    verticalAngleRad: ANGLE
  }, {
    horizontalAngleRad: 0.01731877634,
    verticalAngleRad: ANGLE
  }, DISTANCE);
  expect(x).toBeCloseTo((1 / 2) * DISTANCE, 5);
  expect(y).toBeCloseTo(0.43301, 5);
  expect(z).toBeCloseTo(0.75, 5);
});

test("all angles 45°", () => {
  const ANGLE = (1 / 4) * Math.PI;
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  }, {
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  });
  expect(x).toBeCloseTo(0.5, 5);
  expect(y).toBeCloseTo(0.35355, 5);
  expect(z).toBeCloseTo(0.35355, 5);
});

test("all angles 10°", () => {
  const ANGLE = (1 / 18) * Math.PI;
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  }, {
    horizontalAngleRad: ANGLE,
    verticalAngleRad: ANGLE
  });
  expect(x).toBeCloseTo(0.5, 5);
  expect(y).toBeCloseTo(0.08682, 5);
  expect(z).toBeCloseTo(0.01531, 5);
});

test("all angles garbage degrees (33°, 12° and 84°, 12°)", () => {
  const { x, y, z } = calculateCoordinates({
    horizontalAngleRad: (33 / 180) * Math.PI,
    verticalAngleRad: (12 / 180) * Math.PI
  }, {
    horizontalAngleRad: (84 / 180) * Math.PI,
    verticalAngleRad: (12 / 180) * Math.PI
  });
  expect(x).toBeCloseTo(0.93611, 5);
  expect(y).toBeCloseTo(0.59463, 5);
  expect(z).toBeCloseTo(0.12639, 5);
});

test("doc example", () => {
  expect(calculateCoordinates({
    horizontalAngleRad: (63.4 / 180) * Math.PI,
    verticalAngleRad: (30 / 180) * Math.PI
  }, {
    horizontalAngleRad: (40.6 / 180) * Math.PI,
    verticalAngleRad: (30 / 180) * Math.PI
  })).toEqual({
    x: 0.30031,
    y: 0.51936,
    z: 0.29985
  })
});
