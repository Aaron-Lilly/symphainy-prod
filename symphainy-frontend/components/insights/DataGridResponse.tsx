import React from "react";

interface DataGridResponseProps {
  columnDefs: any[];
  rowData: any[];
}

const DataGridResponse: React.FC<DataGridResponseProps> = ({
  columnDefs,
  rowData,
}) => {
  if (
    !Array.isArray(columnDefs) ||
    !Array.isArray(rowData) ||
    columnDefs.length === 0
  ) {
    return <div className="text-gray-500 italic">No data available.</div>;
  }
  return (
    <div className="overflow-x-auto border rounded">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            {columnDefs.map((col, i) => (
              <th
                key={i}
                className="px-3 py-2 font-semibold text-left border-b"
              >
                {col.headerName || col.field || `Col ${i + 1}`}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rowData.length === 0 ? (
            <tr>
              <td
                colSpan={columnDefs.length}
                className="text-center py-4 text-gray-400"
              >
                No rows
              </td>
            </tr>
          ) : (
            rowData.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                {columnDefs.map((col, j) => (
                  <td key={j} className="px-3 py-2 border-b">
                    {row[col.field] ?? ""}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataGridResponse;
