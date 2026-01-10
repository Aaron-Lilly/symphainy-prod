import "@testing-library/jest-dom";
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FileUploader from "../components/content/FileUploader";

jest.mock("../lib/api/fms", () => ({
  uploadFile: jest.fn(() => Promise.resolve()),
}));

describe("FileUploader", () => {
  it("renders all file type tiles", () => {
    render(<FileUploader />);
    expect(
      screen.getByRole("button", { name: "Structured" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Image" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "PDF" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Mainframe" }),
    ).toBeInTheDocument();
  });

  it("enables dropzone after tile selection", () => {
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Structured" }));
    expect(
      screen.getByText(/Drop or select a Structured file/),
    ).toBeInTheDocument();
  });

  it("shows copybook prompt for Mainframe", () => {
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Mainframe" }));
    expect(screen.getByText(/Copybook File/)).toBeInTheDocument();
  });

  it("disables upload button if no file selected", () => {
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Structured" }));
    expect(screen.queryByText("Upload")).not.toBeInTheDocument();
  });

  it("shows error if copybook missing for Mainframe", async () => {
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Mainframe" }));
    // Simulate file selection
    const dropzone = screen.getByText(
      /Drop or select a Mainframe file/,
    ).parentElement;
    Object.defineProperty(dropzone, "files", {
      value: [
        new File([""], "mainframe.dat", { type: "application/octet-stream" }),
      ],
    });
    fireEvent.drop(dropzone);
    // Try to upload without copybook
    const uploadBtn = screen.queryByText("Upload");
    if (uploadBtn) fireEvent.click(uploadBtn);
    await waitFor(() => {
      expect(
        screen.getByText(/Please upload a copybook file/),
      ).toBeInTheDocument();
    });
  });

  it("shows upload success message", async () => {
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Structured" }));
    // Simulate file selection
    const dropzone = screen.getByText(
      /Drop or select a Structured file/,
    ).parentElement;
    Object.defineProperty(dropzone, "files", {
      value: [new File([""], "test.csv", { type: "text/csv" })],
    });
    fireEvent.drop(dropzone);
    // Simulate upload
    const uploadBtn = screen.queryByText("Upload");
    if (uploadBtn) fireEvent.click(uploadBtn);
    await waitFor(() => {
      expect(screen.getByText("Upload successful!")).toBeInTheDocument();
    });
  });

  it("shows upload error message", async () => {
    const { uploadFile } = require("../lib/api/fms");
    uploadFile.mockImplementationOnce(() =>
      Promise.reject(new Error("Upload failed.")),
    );
    render(<FileUploader />);
    fireEvent.click(screen.getByRole("button", { name: "Structured" }));
    // Simulate file selection
    const dropzone = screen.getByText(
      /Drop or select a Structured file/,
    ).parentElement;
    Object.defineProperty(dropzone, "files", {
      value: [new File([""], "test.csv", { type: "text/csv" })],
    });
    fireEvent.drop(dropzone);
    // Simulate upload
    const uploadBtn = screen.queryByText("Upload");
    if (uploadBtn) fireEvent.click(uploadBtn);
    await waitFor(() => {
      expect(screen.getByText("Upload failed.")).toBeInTheDocument();
    });
  });
});
