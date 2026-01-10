"use client";
import React from "react";
import dynamic from "next/dynamic";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, BarChart3, TrendingUp, PieChart, Activity } from "lucide-react";

// Dynamic imports for different chart libraries
const RechartsBarChart = dynamic(() => import("recharts").then(mod => ({ default: mod.BarChart })), { ssr: false });
const RechartsLineChart = dynamic(() => import("recharts").then(mod => ({ default: mod.LineChart })), { ssr: false });
const RechartsPieChart = dynamic(() => import("recharts").then(mod => ({ default: mod.PieChart })), { ssr: false });
const RechartsAreaChart = dynamic(() => import("recharts").then(mod => ({ default: mod.AreaChart })), { ssr: false });
const RechartsXAxis = dynamic(() => import("recharts").then(mod => ({ default: mod.XAxis })), { ssr: false });
const RechartsYAxis = dynamic(() => import("recharts").then(mod => ({ default: mod.YAxis })), { ssr: false });
const RechartsCartesianGrid = dynamic(() => import("recharts").then(mod => ({ default: mod.CartesianGrid })), { ssr: false });
const RechartsTooltip = dynamic(() => import("recharts").then(mod => mod.Tooltip) as any, { ssr: false });
const RechartsLegend = dynamic(() => import("recharts").then(mod => mod.Legend) as any, { ssr: false });
const RechartsBar = dynamic(() => import("recharts").then(mod => mod.Bar) as any, { ssr: false });
const RechartsLine = dynamic(() => import("recharts").then(mod => mod.Line) as any, { ssr: false });
const RechartsPie = dynamic(() => import("recharts").then(mod => mod.Pie) as any, { ssr: false });
const RechartsCell = dynamic(() => import("recharts").then(mod => mod.Cell) as any, { ssr: false });
const RechartsArea = dynamic(() => import("recharts").then(mod => mod.Area) as any, { ssr: false });
const RechartsResponsiveContainer = dynamic(() => import("recharts").then(mod => ({ default: mod.ResponsiveContainer })), { ssr: false });

// Nivo components for advanced visualizations (only import available ones)
const NivoBar = dynamic(() => import("@nivo/bar").then(mod => ({ default: mod.ResponsiveBar })), { ssr: false });
const NivoLine = dynamic(() => import("@nivo/line").then(mod => ({ default: mod.ResponsiveLine })), { ssr: false });
const NivoHeatmap = dynamic(() => import("@nivo/heatmap").then(mod => ({ default: mod.ResponsiveHeatMap })), { ssr: false });
const NivoScatter = dynamic(() => import("@nivo/scatterplot").then(mod => ({ default: mod.ResponsiveScatterPlot })), { ssr: false });

export interface ChartData {
  [key: string]: any;
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'area' | 'heatmap' | 'scatter';
  library?: 'recharts' | 'nivo';
  title?: string;
  description?: string;
  xAxisKey?: string;
  yAxisKey?: string;
  dataKey?: string;
  colors?: string[];
  height?: number;
  showLegend?: boolean;
  showTooltip?: boolean;
  showGrid?: boolean;
  // Nivo specific config
  nivoConfig?: any;
  // Recharts specific config
  rechartsConfig?: any;
}

export interface ChartProps {
  data: ChartData[] | ChartData;
  config: ChartConfig;
  className?: string;
}

// Color palettes for different chart types
const CHART_COLORS = {
  primary: ['#3b82f6', '#1d4ed8', '#1e40af', '#1e3a8a'],
  success: ['#10b981', '#059669', '#047857', '#065f46'],
  warning: ['#f59e0b', '#d97706', '#b45309', '#92400e'],
  danger: ['#ef4444', '#dc2626', '#b91c1c', '#991b1b'],
  purple: ['#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6'],
  pink: ['#ec4899', '#db2777', '#be185d', '#9d174d'],
  gray: ['#6b7280', '#4b5563', '#374151', '#1f2937'],
};

const getChartIcon = (type: string) => {
  switch (type) {
    case 'bar': return <BarChart3 className="w-4 h-4" />;
    case 'line': return <TrendingUp className="w-4 h-4" />;
    case 'pie': return <PieChart className="w-4 h-4" />;
    case 'area': return <Activity className="w-4 h-4" />;
    default: return <BarChart3 className="w-4 h-4" />;
  }
};

const ChartComponent: React.FC<ChartProps> = ({ data, config, className = "" }) => {
  const {
    type = 'bar',
    library = 'recharts',
    title,
    description,
    height = 300,
    colors = CHART_COLORS.primary,
    showLegend = true,
    showTooltip = true,
    showGrid = true,
    nivoConfig = {},
    rechartsConfig = {},
  } = config;

  // Handle different data formats
  const chartData = Array.isArray(data) ? data : [data];
  
  if (!chartData || chartData.length === 0) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center h-32 text-gray-500">
            <div className="text-center">
              <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">No data available for visualization</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const renderRechartsChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 20, right: 30, left: 20, bottom: 5 },
      ...rechartsConfig,
    };

    switch (type) {
      case 'bar':
        return (
          <RechartsResponsiveContainer width="100%" height={height}>
            <RechartsBarChart {...commonProps}>
              {showGrid && <RechartsCartesianGrid strokeDasharray="3 3" />}
              <RechartsXAxis dataKey={config.xAxisKey || 'name'} />
              <RechartsYAxis />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <RechartsLegend />}
              <RechartsBar {...({ dataKey: config.dataKey || 'value', fill: colors[0] } as any)} />
            </RechartsBarChart>
          </RechartsResponsiveContainer>
        );

      case 'line':
        return (
          <RechartsResponsiveContainer width="100%" height={height}>
            <RechartsLineChart {...commonProps}>
              {showGrid && <RechartsCartesianGrid strokeDasharray="3 3" />}
              <RechartsXAxis dataKey={config.xAxisKey || 'name'} />
              <RechartsYAxis />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <RechartsLegend />}
              <RechartsLine 
                {...({
                  type: "monotone", 
                  dataKey: config.dataKey || 'value', 
                  stroke: colors[0], 
                  strokeWidth: 2
                } as any)}
              />
            </RechartsLineChart>
          </RechartsResponsiveContainer>
        );

      case 'pie':
        return (
          <RechartsResponsiveContainer width="100%" height={height}>
            <RechartsPieChart {...commonProps}>
              <RechartsPie
                {...({
                  data: chartData,
                  dataKey: config.dataKey || 'value',
                  nameKey: config.xAxisKey || 'name',
                  cx: "50%",
                  cy: "50%",
                  outerRadius: 80,
                  fill: "#8884d8",
                  label: true
                } as any)}
              >
                {chartData.map((entry, index) => (
                  <RechartsCell key={`cell-${index}`} {...({ fill: colors[index % colors.length] } as any)} />
                ))}
              </RechartsPie>
              {showTooltip && <RechartsTooltip />}
              {showLegend && <RechartsLegend />}
            </RechartsPieChart>
          </RechartsResponsiveContainer>
        );

      case 'area':
        return (
          <RechartsResponsiveContainer width="100%" height={height}>
            <RechartsAreaChart {...commonProps}>
              {showGrid && <RechartsCartesianGrid strokeDasharray="3 3" />}
              <RechartsXAxis dataKey={config.xAxisKey || 'name'} />
              <RechartsYAxis />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <RechartsLegend />}
              <RechartsArea 
                {...({
                  type: "monotone", 
                  dataKey: config.dataKey || 'value', 
                  stroke: colors[0], 
                  fill: colors[0],
                  fillOpacity: 0.3
                } as any)}
              />
            </RechartsAreaChart>
          </RechartsResponsiveContainer>
        );

      default:
        return (
          <div className="flex items-center justify-center h-32 text-gray-500">
            <p>Unsupported chart type: {type}</p>
          </div>
        );
    }
  };

  const renderNivoChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 50, right: 130, bottom: 50, left: 60 },
      ...nivoConfig,
    };

    switch (type) {
      case 'bar':
        return (
          <div style={{ height: height }}>
            <NivoBar
              {...commonProps}
              keys={[config.dataKey || 'value']}
              indexBy={config.xAxisKey || 'name'}
              colors={colors}
              enableLabel={true}
              labelSkipWidth={12}
              labelSkipHeight={12}
              labelTextColor="inherit:darker(1.4)"
              animate={true}
              motionStiffness={90}
              motionDamping={15}
            />
          </div>
        );

      case 'line':
        return (
          <div style={{ height: height }}>
            <NivoLine
              {...commonProps}
              data={chartData.map((item, index) => ({
                id: item.name || `series-${index}`,
                data: Array.isArray(item.data) ? item.data : [{ x: item.x || index, y: item.y || item.value }]
              }))}
              colors={colors}
              enablePoints={true}
              enableGridX={showGrid}
              enableGridY={showGrid}
              enableSlices="x"
              animate={true}
              motionStiffness={90}
              motionDamping={15}
            />
          </div>
        );

      case 'pie':
        // Use Recharts for pie charts since @nivo/pie is not available
        return (
          <RechartsResponsiveContainer width="100%" height={height}>
            <RechartsPieChart {...commonProps}>
              <RechartsPie
                {...({
                  data: chartData,
                  dataKey: config.dataKey || 'value',
                  nameKey: config.xAxisKey || 'name',
                  cx: "50%",
                  cy: "50%",
                  outerRadius: 80,
                  fill: "#8884d8",
                  label: true
                } as any)}
              >
                {chartData.map((entry, index) => (
                  <RechartsCell key={`cell-${index}`} {...({ fill: colors[index % colors.length] } as any)} />
                ))}
              </RechartsPie>
              {showTooltip && <RechartsTooltip />}
              {showLegend && <RechartsLegend />}
            </RechartsPieChart>
          </RechartsResponsiveContainer>
        );

      case 'heatmap':
        return (
          <div style={{ height: height }}>
            <NivoHeatmap
              {...commonProps}
              data={chartData}
              indexBy="id"
              keys={Object.keys(chartData[0] || {}).filter(key => key !== 'id')}
              colors={colors}
              enableLabels={true}
              animate={true}
              motionStiffness={90}
              motionDamping={15}
            />
          </div>
        );

      case 'scatter':
        return (
          <div style={{ height: height }}>
            <NivoScatter
              {...commonProps}
              data={chartData.map((item, index) => ({
                id: item.name || `series-${index}`,
                data: Array.isArray(item.data) ? item.data : [{ x: item.x || index, y: item.y || item.value }]
              }))}
              colors={colors}
              enableGridX={showGrid}
              enableGridY={showGrid}
              animate={true}
              motionStiffness={90}
              motionDamping={15}
            />
          </div>
        );

      default:
        return (
          <div className="flex items-center justify-center h-32 text-gray-500">
            <p>Unsupported chart type: {type}</p>
          </div>
        );
    }
  };

  return (
    <Card className={className}>
      {(title || description) && (
        <div className="p-4 border-b">
          {title && (
            <div className="flex items-center gap-2 mb-1">
              {getChartIcon(type)}
              <h3 className="font-semibold text-gray-900">{title}</h3>
            </div>
          )}
          {description && (
            <p className="text-sm text-gray-600">{description}</p>
          )}
        </div>
      )}
      <CardContent className="pt-6">
        <div className="relative">
          {library === 'nivo' ? renderNivoChart() : renderRechartsChart()}
        </div>
      </CardContent>
    </Card>
  );
};

// Loading wrapper for dynamic imports
const ChartComponentWithLoading: React.FC<ChartProps> = (props) => {
  return (
    <React.Suspense fallback={
      <Card className={props.className}>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center h-32">
            <Loader2 className="animate-spin h-8 w-8 mr-3" />
            <span className="text-gray-600">Loading chart...</span>
          </div>
        </CardContent>
      </Card>
    }>
      <ChartComponent {...props} />
    </React.Suspense>
  );
};

export default ChartComponentWithLoading;
export { ChartComponent, CHART_COLORS };
