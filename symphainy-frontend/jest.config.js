const nextJest = require("next/jest")({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: "./",
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testEnvironment: "jsdom",
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
    "^shared/types/file$": "<rootDir>/../shared/types/file.ts",
    "^shared/(.*)$": "<rootDir>/../shared/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
  },
  testPathIgnorePatterns: ["/node_modules/", "/tests/", "/tests-examples/"],
  transformIgnorePatterns: ["/node_modules/(?!(d3-interpolate|other-es-lib))"],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = nextJest(customJestConfig);
