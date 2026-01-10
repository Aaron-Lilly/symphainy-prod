import React from "react";
import { render, screen } from "@testing-library/react";
import AgentMessage from "../components/insights/AgentMessage";

describe("AgentMessage", () => {
  it("renders agent message content", () => {
    render(<AgentMessage content="Hello from GuideAgent" />);
    expect(screen.getByText("Hello from GuideAgent")).toBeInTheDocument();
  });
});
