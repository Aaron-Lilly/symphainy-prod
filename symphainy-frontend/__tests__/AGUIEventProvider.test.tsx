import React from "react";
import { render, screen, act } from "@testing-library/react";
import {
  AGUIEventProvider,
  useAGUIEvent,
} from "../shared/agui/AGUIEventProvider";

const mockResponse = [
  { type: "agent_message", content: "Hello from GuideAgent" },
];

global.fetch = jest.fn(
  () =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ responses: mockResponse }),
    }) as any,
);

function TestComponent() {
  const { sessionToken, setSessionToken, events, sendEvent } = useAGUIEvent();
  React.useEffect(() => {
    setSessionToken("test-session");
    sendEvent({
      type: "user_message",
      session_token: "test-session",
      content: "Hi",
    });
  }, [setSessionToken, sendEvent]);
  return (
    <div>
      <div data-testid="session">{sessionToken}</div>
      <div data-testid="events">{events.map((e) => e.content).join(",")}</div>
    </div>
  );
}

describe("AGUIEventProvider", () => {
  it("provides sessionToken, sendEvent, and updates events", async () => {
    await act(async () => {
      render(
        <AGUIEventProvider>
          <TestComponent />
        </AGUIEventProvider>,
      );
    });
    expect(screen.getByTestId("session")).toHaveTextContent("test-session");
    // Wait for events to update
    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByTestId("events")).toHaveTextContent(
      "Hello from GuideAgent",
    );
  });
});
