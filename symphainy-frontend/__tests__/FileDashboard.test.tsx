import "@testing-library/jest-dom";
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FileDashboard from "../components/content/FileDashboard";
import { GlobalSessionProvider } from "../shared/agui/GlobalSessionProvider";

// Mock the API functions
global.fetch = jest.fn(() => Promise.reject(new Error("Mock fetch failure")));

jest.mock("../lib/api/fms", () => ({
  listFiles: jest.fn().mockResolvedValue([
    {
      file_uuid: "1",
      file_name: "data1.csv",
      file_type: "csv",
      created_at: new Date().toISOString(),
    },
    {
      file_uuid: "2",
      file_name: "data2.csv",
      file_type: "csv",
      created_at: new Date().toISOString(),
    },
  ]),
  deleteFile: jest.fn(() => Promise.resolve()),
}));

describe("FileDashboard", () => {
  it("renders mock files in table", async () => {
    render(
      <GlobalSessionProvider>
        <FileDashboard />
      </GlobalSessionProvider>,
    );
    expect(await screen.findByText("data1.csv")).toBeInTheDocument();
    expect(await screen.findByText("Delete")).toBeInTheDocument();
  });

  it("shows confirmation modal on delete", async () => {
    render(
      <GlobalSessionProvider>
        <FileDashboard />
      </GlobalSessionProvider>,
    );
    fireEvent.click((await screen.findAllByText("Delete"))[0]);
    expect(
      await screen.findByText(/Are you sure you want to delete/),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByText("Cancel"));
    expect(
      screen.queryByText(/Are you sure you want to delete/),
    ).not.toBeInTheDocument();
  });

  it("deletes a file and updates the table", async () => {
    render(
      <GlobalSessionProvider>
        <FileDashboard />
      </GlobalSessionProvider>,
    );
    fireEvent.click((await screen.findAllByText("Delete"))[0]);
    fireEvent.click(await screen.findByText("Confirm"));
    await waitFor(() => {
      expect(screen.queryByText("data1.csv")).not.toBeInTheDocument();
    });
  });

  it("renders empty state if no files", async () => {
    // We need to mock listFiles to return an empty array for this test.
    require("../lib/api/fms").listFiles.mockResolvedValueOnce([]);
    render(
      <GlobalSessionProvider>
        <FileDashboard />
      </GlobalSessionProvider>,
    );
    expect(await screen.findByText("No files found.")).toBeInTheDocument();
  });
});
