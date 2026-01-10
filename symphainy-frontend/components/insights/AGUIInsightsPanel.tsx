import React, { useState, useEffect } from "react";
// import { AGUIClientProvider, AGUIWorkspace } from '@ag-ui/react'; // TODO: Restore after AG-UI is installed
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAGUIEvent } from "@/shared/agui/AGUIEventProvider";
import SummaryOutput from "./SummaryOutput";
import DataGridResponse from "./DataGridResponse";
import VisualOutput from "./VisualOutput";
import AgentMessage from "./AgentMessage";
import ErrorMessage from "./ErrorMessage";
import { ResponsiveHeatMap } from "@nivo/heatmap";
import { ResponsiveBar } from "@nivo/bar";
import { ResponsiveLine } from "@nivo/line";
import { ResponsiveScatterPlot } from "@nivo/scatterplot";

interface AGUIInsightsPanelProps {
  onClose?: () => void;
}

interface GridData {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

interface Visualization {
  type: string;
  title?: string;
  description?: string;
  data: any;
  xKey?: string;
  yKey?: string;
  valueKey?: string;
  keys?: string[];
  rationale?: string;
  nivoChartType?: string;
  // Add other config fields as needed
}

interface Alert {
  level: "info" | "warning" | "critical";
  message: string;
  recommendation?: string;
}

interface InsightsPanelOutput {
  summary: string;
  grid: GridData;
  visualizations: Visualization[];
  alerts: Alert[];
  metadata?: Record<string, any>;
}

const MAX_OUTPUTS = 3;

function processAGUIResponsesStacked(responses: any[]) {
  // Collect all outputs by type
  const result: Record<string, any[]> = {
    summary_output: [],
    data_grid_response: [],
    visual_output: [],
    agent_message: [],
    error: [],
  };
  for (const resp of responses) {
    if (resp.type && result[resp.type] !== undefined) {
      result[resp.type].push(resp);
    }
  }
  return result;
}

// Enhanced table for grid data with sorting and filtering
function SimpleDataTable({
  columns,
  rows,
}: {
  columns: string[];
  rows: any[][];
}) {
  const [sortCol, setSortCol] = React.useState<number | null>(null);
  const [sortAsc, setSortAsc] = React.useState(true);
  const [filter, setFilter] = React.useState("");

  // Filtered and sorted rows
  const displayedRows = React.useMemo(() => {
    let filtered = rows;
    if (filter) {
      filtered = filtered.filter((row) =>
        row.some((cell) =>
          String(cell).toLowerCase().includes(filter.toLowerCase()),
        ),
      );
    }
    if (sortCol !== null) {
      filtered = [...filtered].sort((a, b) => {
        if (a[sortCol] === b[sortCol]) return 0;
        if (a[sortCol] == null) return 1;
        if (b[sortCol] == null) return -1;
        if (a[sortCol]! < b[sortCol]!) return sortAsc ? -1 : 1;
        return sortAsc ? 1 : -1;
      });
    }
    return filtered;
  }, [rows, filter, sortCol, sortAsc]);

  if (!columns || columns.length === 0)
    return <div className="text-gray-500 italic">No columns.</div>;
  if (!rows || rows.length === 0)
    return <div className="text-gray-500 italic">No rows.</div>;

  return (
    <div className="overflow-x-auto border rounded">
      <div className="p-2">
        <input
          type="text"
          placeholder="Filter rows..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border px-2 py-1 rounded text-sm mb-2 w-full"
        />
      </div>
      <table className="min-w-full text-sm" role="table">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((col, i) => (
              <th
                key={i}
                className="px-3 py-2 font-semibold text-left border-b cursor-pointer select-none"
                onClick={() => {
                  if (sortCol === i) setSortAsc((a) => !a);
                  else {
                    setSortCol(i);
                    setSortAsc(true);
                  }
                }}
                aria-sort={
                  sortCol === i
                    ? sortAsc
                      ? "ascending"
                      : "descending"
                    : "none"
                }
                tabIndex={0}
              >
                {col}
                {sortCol === i ? (sortAsc ? " ▲" : " ▼") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayedRows.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="text-center py-4 text-gray-400"
              >
                No rows match filter.
              </td>
            </tr>
          ) : (
            displayedRows.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                {row.map((cell, j) => (
                  <td key={j} className="px-3 py-2 border-b">
                    {String(cell)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function AGUIInsightsPanel({ onClose }: AGUIInsightsPanelProps) {
  const { sessionToken, events, sendEvent } = useAGUIEvent();
  const [activeTab, setActiveTab] = useState({
    summary: 0,
    grid: 0,
    visual: 0,
  });
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState<InsightsPanelOutput | null>(null);
  const [error, setError] = useState<string | null>(null);

  // On mount, send initial tool_invocation event
  useEffect(() => {
    if (!sessionToken) return;
    setLoading(true);
    setError(null);
    const sendAgentEvent = async (event) => {
      const resp = await fetch("/global/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_token: sessionToken,
          agent_type: event.agent_type || "GuideAgent",
          pillar: "insights",
          event,
        }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      return resp.json();
    };
    sendAgentEvent({ type: "user_message", content: "Show me insights" })
      .then((data) => {
        try {
          if (Array.isArray(data.responses)) {
            const outputs = processAGUIResponsesStacked(data.responses);
            setOutput({
              summary:
                outputs.summary_output[0]?.summary || "No summary available.",
              grid: outputs.data_grid_response[0]
                ? {
                    columns:
                      outputs.data_grid_response[0].columnDefs?.map(
                        (c: any) => c.headerName,
                      ) || [],
                    rows:
                      outputs.data_grid_response[0].rowData?.map((row: any) =>
                        Object.values(row),
                      ) || [],
                  }
                : { columns: [], rows: [] },
              visualizations: outputs.visual_output || [],
              alerts:
                outputs.error?.map((e: any) => ({
                  level: "info",
                  message: e.message || "Unknown error",
                  recommendation: e.error || "",
                })) || [],
              metadata: {},
            });
          } else {
            setOutput({
              summary: data.summary || "No summary available.",
              grid: data.grid || { columns: [], rows: [] },
              visualizations: data.visualizations || [],
              alerts: data.alerts || [],
              metadata: data.metadata || {},
            });
          }
        } catch (err) {
          setError("Failed to parse insights response.");
          setOutput(null);
        }
      })
      .catch((err) => setError("Failed to load insights."))
      .finally(() => setLoading(false));
  }, [sessionToken]);

  // Process events by type
  const outputs = processAGUIResponsesStacked(events);

  // Helper to render tabs for multiple outputs
  function renderTabbedSection(
    type: string,
    label: string,
    renderFn: (item: any) => React.ReactNode,
  ) {
    const items = outputs[type] || [];
    if (items.length === 0) {
      return (
        <div className="text-gray-500 italic">
          No {label.toLowerCase()} available.
        </div>
      );
    }
    if (items.length === 1) {
      return renderFn(items[0]);
    }
    const capped = items.slice(0, MAX_OUTPUTS);
    return (
      <div>
        <Tabs
          value={String(activeTab[type])}
          onValueChange={(v) =>
            setActiveTab((t) => ({ ...t, [type]: Number(v) }))
          }
        >
          <TabsList>
            {capped.map((_, i) => (
              <TabsTrigger key={i} value={String(i)}>
                {label} {i + 1}
              </TabsTrigger>
            ))}
          </TabsList>
          {capped.map((item, i) => (
            <TabsContent key={i} value={String(i)}>
              {renderFn(item)}
            </TabsContent>
          ))}
        </Tabs>
        {items.length > MAX_OUTPUTS && (
          <div className="text-xs text-gray-400 mt-1">
            Only the first {MAX_OUTPUTS} {label.toLowerCase()}s are shown.
          </div>
        )}
      </div>
    );
  }

  // Debug logs for each section
  console.log(
    "[AGUIInsightsPanel] Rendering Summary Section:",
    outputs.summary_output,
  );
  console.log(
    "[AGUIInsightsPanel] Rendering Data Grid Section:",
    outputs.data_grid_response,
  );
  console.log(
    "[AGUIInsightsPanel] Rendering Visualizations Section:",
    outputs.visual_output,
  );
  if (outputs.error.length > 0) {
    console.log("[AGUIInsightsPanel] Rendering Error Section:", outputs.error);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        Loading insights...
      </div>
    );
  }

  if (error) return <div className="text-red-600">{error}</div>;
  if (!output)
    return <div className="text-gray-500">No insights available.</div>;

  return (
    <div className="flex flex-col h-full p-4 space-y-6 overflow-y-auto">
      <div className="flex justify-between items-center border-b pb-2 mb-2">
        <h2 className="text-xl font-semibold">Data Insights</h2>
        {onClose && (
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        )}
      </div>
      {/* Summary Section */}
      <section data-testid="section-summary">
        <h3 className="text-lg font-semibold mb-2">Summary</h3>
        <div className="bg-gray-50 p-3 rounded">{output.summary}</div>
      </section>
      {/* Grid Section */}
      <section data-testid="section-data-grid">
        <h3 className="text-lg font-semibold mb-2">Data Grid</h3>
        <SimpleDataTable
          columns={output.grid.columns}
          rows={output.grid.rows}
        />
      </section>
      {/* Visualizations Section */}
      <section data-testid="section-visualizations">
        <h3 className="text-lg font-semibold mb-2">Visualizations</h3>
        {output.visualizations.length === 0 ? (
          <div className="text-gray-500 italic">
            No visualizations available.
          </div>
        ) : (
          output.visualizations.map((viz, i) => (
            <VisualizationCard key={i} viz={viz} />
          ))
        )}
      </section>
      {/* Alerts Section */}
      <section data-testid="section-alerts">
        <h3 className="text-lg font-semibold mb-2">Alerts</h3>
        {output.alerts.length === 0 ? (
          <div className="text-gray-500 italic">No alerts.</div>
        ) : (
          output.alerts.map((alert, i) => <AlertCard key={i} alert={alert} />)
        )}
      </section>
      {/* Metadata (optional) */}
      {output.metadata && (
        <section>
          <h3 className="text-lg font-semibold mb-2">Metadata</h3>
          <pre className="bg-gray-100 p-2 rounded text-xs">
            {JSON.stringify(output.metadata, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
}

// Visualization card (stub, extend for real charting)
function VisualizationCard({ viz }: { viz: Visualization }) {
  // Use nivoChartType if present, else fallback to type
  const chartType = viz.nivoChartType || viz.type;

  // Infer keys for heatmap if not provided
  let heatmapKeys: string[] = viz.keys || [];
  if (
    chartType === "heatmap" &&
    (!viz.keys || viz.keys.length === 0) &&
    Array.isArray(viz.data) &&
    viz.data.length > 0
  ) {
    // Collect all unique x values from the data arrays
    const keySet = new Set<string>();
    viz.data.forEach((row: any) => {
      if (Array.isArray(row.data)) {
        row.data.forEach((d: any) => {
          if (d.x !== undefined) keySet.add(String(d.x));
        });
      }
    });
    heatmapKeys = Array.from(keySet);
  }

  // For bar/line/scatter, set keys to all series IDs if multi-series
  let seriesKeys: string[] = [];
  if (
    (chartType === "bar" || chartType === "line" || chartType === "scatter") &&
    Array.isArray(viz.data)
  ) {
    seriesKeys = viz.data.map((series: any) => series.id).filter(Boolean);
  }

  if (chartType === "heatmap") {
    return (
      <div className="mb-4 p-3 border rounded bg-white">
        <div className="font-semibold">{viz.title || viz.type}</div>
        <div className="text-gray-600 text-sm mb-2">{viz.description}</div>
        <div style={{ height: 300 }}>
          <ResponsiveHeatMap
            data={viz.data}
            margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
            colors={{ scheme: "blues", type: "quantize" }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
              legend: viz.xKey,
              legendPosition: "middle",
              legendOffset: 32,
            }}
            axisLeft={{
              legend: viz.yKey,
              legendPosition: "middle",
              legendOffset: -40,
            }}
          />
        </div>
      </div>
    );
  }
  if (chartType === "bar") {
    return (
      <div className="mb-4 p-3 border rounded bg-white">
        <div className="font-semibold">{viz.title || viz.type}</div>
        <div className="text-gray-600 text-sm mb-2">{viz.description}</div>
        <div style={{ height: 300 }}>
          <ResponsiveBar
            data={viz.data}
            keys={seriesKeys.length > 0 ? seriesKeys : [viz.yKey]}
            indexBy={viz.xKey}
            margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
            colors={{ scheme: "nivo" }}
            axisBottom={{
              legend: viz.xKey,
              legendPosition: "middle",
              legendOffset: 32,
            }}
            axisLeft={{
              legend: viz.yKey,
              legendPosition: "middle",
              legendOffset: -40,
            }}
          />
        </div>
      </div>
    );
  }
  if (chartType === "line") {
    return (
      <div className="mb-4 p-3 border rounded bg-white">
        <div className="font-semibold">{viz.title || viz.type}</div>
        <div className="text-gray-600 text-sm mb-2">{viz.description}</div>
        <div style={{ height: 300 }}>
          <ResponsiveLine
            data={viz.data}
            margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
            xScale={{ type: "point" }}
            yScale={{
              type: "linear",
              min: "auto",
              max: "auto",
              stacked: false,
              reverse: false,
            }}
            axisBottom={{
              legend: viz.xKey,
              legendPosition: "middle",
              legendOffset: 32,
            }}
            axisLeft={{
              legend: viz.yKey,
              legendPosition: "middle",
              legendOffset: -40,
            }}
            colors={{ scheme: "nivo" }}
          />
        </div>
      </div>
    );
  }
  if (chartType === "scatter" || chartType === "scatterplot") {
    return (
      <div className="mb-4 p-3 border rounded bg-white">
        <div className="font-semibold">{viz.title || viz.type}</div>
        <div className="text-gray-600 text-sm mb-2">{viz.description}</div>
        <div style={{ height: 300 }}>
          <ResponsiveScatterPlot
            data={viz.data}
            margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
            xScale={{ type: "linear", min: "auto", max: "auto" }}
            yScale={{ type: "linear", min: "auto", max: "auto" }}
            axisBottom={{
              legend: viz.xKey,
              legendPosition: "middle",
              legendOffset: 32,
            }}
            axisLeft={{
              legend: viz.yKey,
              legendPosition: "middle",
              legendOffset: -40,
            }}
            colors={{ scheme: "nivo" }}
          />
        </div>
      </div>
    );
  }
  // Fallback: show JSON
  return (
    <div className="mb-4 p-3 border rounded bg-white">
      <div className="font-semibold">{viz.title || viz.type}</div>
      <div className="text-gray-600 text-sm mb-2">{viz.description}</div>
      <pre className="bg-gray-100 p-2 rounded text-xs">
        {JSON.stringify(viz.data, null, 2)}
      </pre>
    </div>
  );
}

// Alert card
function AlertCard({ alert }: { alert: Alert }) {
  const color =
    alert.level === "critical"
      ? "bg-red-100 text-red-800"
      : alert.level === "warning"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-blue-100 text-blue-800";
  return (
    <div className={`mb-2 p-2 rounded ${color}`}>
      <div className="font-semibold">{alert.level.toUpperCase()}</div>
      <div>{alert.message}</div>
      {alert.recommendation && (
        <div className="italic text-xs mt-1">{alert.recommendation}</div>
      )}
    </div>
  );
}
