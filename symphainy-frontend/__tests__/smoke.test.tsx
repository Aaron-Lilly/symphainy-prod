import React from "react";
import { render, screen } from "@testing-library/react";

// Simple smoke test to verify Jest is working
describe("Smoke Test", () => {
  it("renders a basic React component", () => {
    const TestComponent = () => <div data-testid="smoke-test">Smoke Test Passed</div>;
    render(<TestComponent />);
    expect(screen.getByTestId("smoke-test")).toBeInTheDocument();
    expect(screen.getByText(/Smoke Test Passed/i)).toBeInTheDocument();
  });

  it("Jest matchers work correctly", () => {
    expect(true).toBe(true);
    expect([1, 2, 3]).toHaveLength(3);
    expect({ a: 1 }).toHaveProperty("a", 1);
  });
});
