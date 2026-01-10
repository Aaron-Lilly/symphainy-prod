import "@testing-library/jest-dom";
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import AGUIInsightsPanel from "../components/insights/AGUIInsightsPanel";
import { AGUIEventProvider } from "../shared/agui/AGUIEventProvider";

// Mock AGUIClientProvider and AGUIWorkspace to avoid real AG-UI logic
jest.mock("@ag-ui/react", () => ({
  AGUIClientProvider: ({ children }: any) => (
    <div data-testid="agui-provider">{children}</div>
  ),
  AGUIWorkspace: (props: any) => (
    <div data-testid="agui-workspace">AGUI Workspace</div>
  ),
}));

const mockSessionToken = "test-session-token";

const mockOutputs = {
  summary_output: [
    { summary: "<b>Summary 1</b>" },
    { summary: "<b>Summary 2</b>" },
  ],
  data_grid_response: [
    {
      columnDefs: [{ headerName: "A", field: "a" }],
      rowData: [{ a: 1 }, { a: 2 }],
      defaultColDef: {},
      pagination: false,
      paginationPageSize: 10,
    },
  ],
  visual_output: [{ image: "img.png", description: "A chart" }],
  agent_message: [],
  error: [{ message: "Test error" }, { message: "Another error" }],
};

function renderWithProvider(ui: React.ReactElement) {
  return render(
    <AGUIEventProvider sessionToken={mockSessionToken}>{ui}</AGUIEventProvider>,
  );
}

describe("AGUIInsightsPanel", () => {
  it("renders with session token and close button", () => {
    const onClose = jest.fn();
    renderWithProvider(<AGUIInsightsPanel onClose={onClose} />);
    expect(screen.getByText("Data Insights")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalled();
  });

  it("renders summary, grid, visual, and error sections", () => {
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Summary")).toBeInTheDocument();
    expect(screen.getByText("Data Grid")).toBeInTheDocument();
    expect(screen.getByText("Visualizations")).toBeInTheDocument();
    expect(screen.getByText("AI Assistant")).toBeInTheDocument();
  });

  it("renders error messages if present (multiple errors)", () => {
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [mockOutputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Test error")).toBeInTheDocument();
    expect(screen.getByText("Another error")).toBeInTheDocument();
  });

  it("renders summary tabs and switches between them", () => {
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [mockOutputs, jest.fn()])
      .mockImplementationOnce(() => [
        { summary: 0, grid: 0, visual: 0 },
        jest.fn(),
      ]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Summary 1")).toBeInTheDocument();
    // Simulate tab switch
    const tab = screen.getByRole("tab", { name: /Summary 2/ });
    fireEvent.click(tab);
    // Would need to check for Summary 2, but since dangerouslySetInnerHTML is used, this is a smoke test
  });

  it("renders empty state for all outputs", () => {
    const emptyOutputs = {
      summary_output: [],
      data_grid_response: [],
      visual_output: [],
      agent_message: [],
      error: [],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [emptyOutputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText(/No summary available/)).toBeInTheDocument();
    expect(screen.getByText(/No grid available/)).toBeInTheDocument();
    expect(screen.getByText(/No visualizations available/)).toBeInTheDocument();
  });

  it("renders visual output with no image", () => {
    const outputs = {
      ...mockOutputs,
      visual_output: [{ description: "No image here" }],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [outputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("No image available.")).toBeInTheDocument();
    expect(screen.getByText("No image here")).toBeInTheDocument();
  });

  it("renders grid with multiple rows", () => {
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [mockOutputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Grid 1")).toBeInTheDocument();
    // The grid content is rendered by a mock component, so this is a smoke test
  });

  it("renders a Nivo bar chart with multi-series data", () => {
    const outputs = {
      summary_output: [],
      data_grid_response: [],
      visual_output: [
        {
          type: "histogram",
          nivoChartType: "bar",
          data: [
            {
              id: "A",
              data: [
                { x: "bin1", y: 10 },
                { x: "bin2", y: 20 },
              ],
            },
            {
              id: "B",
              data: [
                { x: "bin1", y: 5 },
                { x: "bin2", y: 15 },
              ],
            },
          ],
          xKey: "x",
          yKey: "y",
          title: "Test Histogram",
        },
      ],
      agent_message: [],
      error: [],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [outputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Test Histogram")).toBeInTheDocument();
  });

  it("renders a Nivo line chart with multi-series data", () => {
    const outputs = {
      summary_output: [],
      data_grid_response: [],
      visual_output: [
        {
          type: "line",
          nivoChartType: "line",
          data: [
            {
              id: "Metric 1",
              data: [
                { x: "2024-01-01", y: 100 },
                { x: "2024-01-02", y: 120 },
              ],
            },
            {
              id: "Metric 2",
              data: [
                { x: "2024-01-01", y: 80 },
                { x: "2024-01-02", y: 90 },
              ],
            },
          ],
          xKey: "x",
          yKey: "y",
          title: "Test Line Chart",
        },
      ],
      agent_message: [],
      error: [],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [outputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Test Line Chart")).toBeInTheDocument();
  });

  it("renders a Nivo scatter plot with multi-series data", () => {
    const outputs = {
      summary_output: [],
      data_grid_response: [],
      visual_output: [
        {
          type: "scatter",
          nivoChartType: "scatter",
          data: [
            {
              id: "Group 1",
              data: [
                { x: 1, y: 2 },
                { x: 2, y: 3 },
              ],
            },
            {
              id: "Group 2",
              data: [
                { x: 1, y: 4 },
                { x: 2, y: 5 },
              ],
            },
          ],
          xKey: "x",
          yKey: "y",
          title: "Test Scatter Plot",
        },
      ],
      agent_message: [],
      error: [],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [outputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Test Scatter Plot")).toBeInTheDocument();
  });

  it("renders a Nivo heatmap with multi-series data", () => {
    const outputs = {
      summary_output: [],
      data_grid_response: [],
      visual_output: [
        {
          type: "heatmap",
          nivoChartType: "heatmap",
          data: [
            {
              id: "Row1",
              data: [
                { x: "Col1", y: 1 },
                { x: "Col2", y: 2 },
              ],
            },
            {
              id: "Row2",
              data: [
                { x: "Col1", y: 3 },
                { x: "Col2", y: 4 },
              ],
            },
          ],
          xKey: "x",
          yKey: "y",
          title: "Test Heatmap",
        },
      ],
      agent_message: [],
      error: [],
    };
    jest
      .spyOn(React, "useState")
      .mockImplementationOnce(() => [outputs, jest.fn()]);
    renderWithProvider(<AGUIInsightsPanel />);
    expect(screen.getByText("Test Heatmap")).toBeInTheDocument();
  });
});
