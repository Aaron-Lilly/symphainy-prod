import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import ParsePreview from "../components/content/ParsePreview";
import { AppProvider } from "@/shared/agui/AppProvider";
import { SessionProvider } from "@/shared/agui/SessionProvider";
import { FileMetadata, FileStatus } from "shared/types/file";
import { parseFile, approveFile, rejectFile } from "@/lib/api/fms";

// Mock the Next.js router
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock the API functions
jest.mock("@/lib/api/fms");
const mockedParseFile = parseFile as jest.Mock;
const mockedApproveFile = approveFile as jest.Mock;
const mockedRejectFile = rejectFile as jest.Mock;

const mockFiles: FileMetadata[] = [
  {
    uuid: "1",
    name: "test.csv",
    ui_name: "test.csv",
    file_type: "csv",
    status: FileStatus.Uploaded,
    created_at: new Date().toISOString(),
    metadata: {},
  },
  {
    uuid: "2",
    name: "test2.csv",
    ui_name: "test2.csv",
    file_type: "csv",
    status: FileStatus.Uploaded,
    created_at: new Date().toISOString(),
    metadata: {},
  },
];

const renderWithProviders = (
  ui: React.ReactElement,
  files: FileMetadata[] = mockFiles,
) => {
  return render(
    <SessionProvider>
      <AppProvider initialFiles={files}>{ui}</AppProvider>
    </SessionProvider>,
  );
};

describe("ParsePreview", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedParseFile.mockResolvedValue({
      preview_grid: [
        ["R1C1", "R1C2"],
        ["R2C1", "R2C2"],
      ],
      metadata: { columns: 2, rows: 2 },
    });
    mockedApproveFile.mockResolvedValue({ success: true });
    mockedRejectFile.mockResolvedValue({ success: true });
  });

  it("renders dropdown and allows file selection", async () => {
    renderWithProviders(<ParsePreview />);

    expect(await screen.findByText("test.csv")).toBeInTheDocument();

    const select = screen.getByTestId("parse-dropdown");
    fireEvent.keyDown(select.childNodes[0], { key: "ArrowDown" });
    await waitFor(() => screen.getByText("test2.csv"));
    fireEvent.click(screen.getByText("test2.csv"));

    // Just check the value updated in the select
    expect(await screen.findByText("test2.csv")).toBeInTheDocument();
  });

  it("parses a file and displays the results", async () => {
    renderWithProviders(<ParsePreview />);

    const parseButton = screen.getByRole("button", {
      name: /Parse Selected File/i,
    });
    fireEvent.click(parseButton);

    expect(mockedParseFile).toHaveBeenCalledWith("1", undefined);
    expect(await screen.findByText("File Metadata")).toBeInTheDocument();
    expect(await screen.findByText(/R1C1/)).toBeInTheDocument();
  });

  it("handles approve action", async () => {
    renderWithProviders(<ParsePreview />);

    const parseButton = screen.getByRole("button", {
      name: /Parse Selected File/i,
    });
    fireEvent.click(parseButton);
    await screen.findByText("File Metadata");

    const approveButton = screen.getByRole("button", { name: /Approve/i });
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockedApproveFile).toHaveBeenCalledWith(
        "1",
        { uuid: "1" },
        undefined,
      );
    });
  });

  it("handles reject action", async () => {
    renderWithProviders(<ParsePreview />);

    const parseButton = screen.getByRole("button", {
      name: /Parse Selected File/i,
    });
    fireEvent.click(parseButton);
    await screen.findByText("File Metadata");

    const rejectButton = screen.getByRole("button", { name: /Reject/i });
    fireEvent.click(rejectButton);

    // This will open the modal, let's type a reason and submit
    const reasonTextarea = screen.getByPlaceholderText(
      /Provide a reason for rejection/i,
    );
    fireEvent.change(reasonTextarea, {
      target: { value: "Test rejection reason" },
    });

    const confirmRejectButton = screen.getByRole("button", {
      name: /Confirm Reject/i,
    });
    fireEvent.click(confirmRejectButton);

    await waitFor(() => {
      expect(mockedRejectFile).toHaveBeenCalledWith(
        "1",
        { uuid: "1", reason: "Test rejection reason" },
        undefined,
      );
    });
  });
});
