import React from "react";
import { render, screen } from "@testing-library/react";
import SummaryOutput from "../components/insights/SummaryOutput";

describe("SummaryOutput", () => {
  it("renders HTML summary content", () => {
    render(<SummaryOutput summary="<b>Test Summary</b>" />);
    expect(screen.getByText("Test Summary")).toBeInTheDocument();
  });
  it("renders empty container for empty summary", () => {
    const { container } = render(<SummaryOutput summary="" />);
    // Should render the wrapper div but with no content
    const wrapper = container.querySelector('.prose');
    expect(wrapper).toBeInTheDocument();
    expect(wrapper?.innerHTML).toBe('');
  });
});
