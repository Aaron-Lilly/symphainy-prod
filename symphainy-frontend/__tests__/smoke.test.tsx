import React from "react";
import { render, screen } from "@testing-library/react";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders welcome message", () => {
    render(<HomePage />);
    expect(screen.getByText(/Welcome to SymphAIny/i)).toBeInTheDocument();
  });
});
