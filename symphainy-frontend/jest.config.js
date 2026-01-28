const nextJest = require("next/jest");

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: "./",
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testEnvironment: "jsdom",
  moduleNameMapper: {
    // Mock old session providers that have been replaced
    "^@/shared/agui/GlobalSessionProvider$": "<rootDir>/__mocks__/providers.js",
    "^@/shared/agui/SessionProvider$": "<rootDir>/__mocks__/providers.js",
    "^@/shared/components/SessionProvider$": "<rootDir>/__mocks__/providers.js",
    "^\\.\\./shared/components/SessionProvider$": "<rootDir>/__mocks__/providers.js",
    "^\\.\\./shared/agui/GlobalSessionProvider$": "<rootDir>/__mocks__/providers.js",
    "^\\.\\./shared/agui/SessionProvider$": "<rootDir>/__mocks__/providers.js",
    // Main path mapping
    "^@/(.*)$": "<rootDir>/$1",
    "^shared/types/file$": "<rootDir>/../shared/types/file.ts",
    "^shared/(.*)$": "<rootDir>/../shared/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    // Mock nivo and d3 modules that use ESM syntax
    "@nivo/(.*)": "<rootDir>/__mocks__/nivo.js",
    "d3-(.*)": "<rootDir>/__mocks__/d3.js",
  },
  testPathIgnorePatterns: [
    "/node_modules/",
    "/tests/",
    "/tests-examples/",
    "/__tests__/utils/",
    "/e2e/",
    "/scripts/",
    "\\.spec\\.ts$",  // Playwright tests use .spec.ts
    "shared/config/environments/",  // Environment config files
    "components/content/SimpleFileDashboard\\.test",  // Missing component test
  ],
  transformIgnorePatterns: [
    "/node_modules/(?!(@nivo|d3-.*|d3|internmap|delaunator|robust-predicates)/)",
  ],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig);
