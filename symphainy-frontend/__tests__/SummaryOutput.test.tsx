import React from "react";
import { render, screen } from "@testing-library/react";
import SummaryOutput from "../components/insights/SummaryOutput";

describe("SummaryOutput", () => {
  it("renders HTML summary content", () => {
    render(<SummaryOutput summary="<b>Test Summary</b>" />);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });
  it("renders nothing for empty summary", () => {
    render(<SummaryOutput summary="" />);
    expect(screen.getByText("")).toBeInTheDocument();
  });
});
