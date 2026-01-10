import React from "react";
import { render, screen } from "@testing-library/react";
import DataGridResponse from "../components/insights/DataGridResponse";

describe("DataGridResponse", () => {
  it("renders table with headers and rows", () => {
    const columnDefs = [
      { headerName: "A", field: "a" },
      { headerName: "B", field: "b" },
    ];
    const rowData = [
      { a: 1, b: 2 },
      { a: 3, b: 4 },
    ];
    render(<DataGridResponse columnDefs={columnDefs} rowData={rowData} />);
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("B")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });
  it("renders empty state for no data", () => {
    render(<DataGridResponse columnDefs={[]} rowData={[]} />);
    expect(screen.getByText(/No data available/)).toBeInTheDocument();
  });
});
