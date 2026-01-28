require("@testing-library/jest-dom");
require("whatwg-fetch");

if (typeof global.TextEncoder === "undefined") {
  global.TextEncoder = require("util").TextEncoder;
}
if (typeof global.TextDecoder === "undefined") {
  global.TextDecoder = require("util").TextDecoder;
}

// Default fetch mock - returns a reasonable default response
// Tests can override this with jest.spyOn or mockImplementation
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ success: true, data: null }),
    text: () => Promise.resolve(''),
    headers: new Headers(),
  })
);

// Reset fetch mock before each test
beforeEach(() => {
  global.fetch.mockClear();
});
