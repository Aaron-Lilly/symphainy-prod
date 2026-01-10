require("@testing-library/jest-dom");
require("whatwg-fetch");

if (typeof global.TextEncoder === "undefined") {
  global.TextEncoder = require("util").TextEncoder;
}
if (typeof global.TextDecoder === "undefined") {
  global.TextDecoder = require("util").TextDecoder;
}

global.fetch = jest.fn(() => Promise.reject(new Error("Mock fetch failure")));
