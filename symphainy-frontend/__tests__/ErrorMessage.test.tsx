import React from "react";
import { render, screen } from "@testing-library/react";
import ErrorMessage from "../components/insights/ErrorMessage";

describe("ErrorMessage", () => {
  it("renders error message", () => {
    render(<ErrorMessage message="Something went wrong" />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });
  it("renders fallback for empty message", () => {
    render(<ErrorMessage message="" />);
    expect(screen.getByText("Unknown error.")).toBeInTheDocument();
  });
});
