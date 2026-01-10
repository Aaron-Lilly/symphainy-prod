import React from "react";
import { render, screen } from "@testing-library/react";
import VisualOutput from "../components/insights/VisualOutput";

describe("VisualOutput", () => {
  it("renders image and description", () => {
    render(<VisualOutput image="img.png" description="A chart" />);
    expect(screen.getByAltText("A chart")).toBeInTheDocument();
    expect(screen.getByText("A chart")).toBeInTheDocument();
  });
  it("renders empty state for no image", () => {
    render(<VisualOutput description="No image here" />);
    expect(screen.getByText(/No visual available/)).toBeInTheDocument();
    expect(screen.getByText("No image here")).toBeInTheDocument();
  });
});
