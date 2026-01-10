import React from "react";
import { render, act } from "@testing-library/react";
import {
  GlobalSessionProvider,
  useGlobalSession,
} from "../shared/agui/GlobalSessionProvider";

function TestComponent() {
  const {
    guideSessionToken,
    setGuideSessionToken,
    getPillarState,
    setPillarState,
    resetAllState,
  } = useGlobalSession();
  return (
    <div>
      <div data-testid="token">{guideSessionToken}</div>
      <div data-testid="pillar">
        {JSON.stringify(getPillarState("insights"))}
      </div>
      <button onClick={async () => await setGuideSessionToken("test-token")}>
        Set Token
      </button>
      <button
        onClick={async () => await setPillarState("insights", { foo: "bar" })}
      >
        Set Pillar
      </button>
      <button onClick={async () => await resetAllState()}>Reset</button>
    </div>
  );
}

describe("GlobalSessionProvider", () => {
  it("persists and restores session token and pillar state", async () => {
    const { getByText, getByTestId } = render(
      <GlobalSessionProvider>
        <TestComponent />
      </GlobalSessionProvider>,
    );

    // Initially null
    expect(getByTestId("token").textContent).toBe("");
    expect(getByTestId("pillar").textContent).toBe("null");

    // Set token
    await act(async () => {
      getByText("Set Token").click();
    });
    expect(getByTestId("token").textContent).toBe("test-token");

    // Set pillar state
    await act(async () => {
      getByText("Set Pillar").click();
    });
    expect(getByTestId("pillar").textContent).toBe(
      JSON.stringify({ foo: "bar" }),
    );

    // Reset all
    await act(async () => {
      getByText("Reset").click();
    });
    expect(getByTestId("token").textContent).toBe("");
    expect(getByTestId("pillar").textContent).toBe("null");
  });
});
