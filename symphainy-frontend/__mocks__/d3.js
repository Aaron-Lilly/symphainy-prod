// Mock for d3 libraries
module.exports = {
  interpolate: () => () => 0,
  interpolateNumber: () => () => 0,
  interpolateString: () => () => '',
  interpolateArray: () => () => [],
  interpolateRgb: () => () => '#000000',
  scaleLinear: () => ({
    domain: () => ({ range: () => () => 0 }),
  }),
  // Add other common d3 exports as needed
};
