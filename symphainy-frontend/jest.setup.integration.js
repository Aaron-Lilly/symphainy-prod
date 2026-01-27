// Integration test setup - NO fetch mocking
// This allows real backend calls

require("@testing-library/jest-dom");
require("whatwg-fetch");

if (typeof global.TextEncoder === "undefined") {
  global.TextEncoder = require("util").TextEncoder;
}
if (typeof global.TextDecoder === "undefined") {
  global.TextDecoder = require("util").TextDecoder;
}

// DO NOT mock fetch - we need real fetch for integration tests
// global.fetch is left as Node's built-in fetch (Node 18+)
