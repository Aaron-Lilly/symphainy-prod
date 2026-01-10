import React from "react";

interface VisualOutputProps {
  image?: string;
  description?: string;
}

const VisualOutput: React.FC<VisualOutputProps> = ({ image, description }) => (
  <div className="flex flex-col items-center">
    {image ? (
      <img
        src={image}
        alt={description || "Visualization"}
        className="max-h-64 max-w-full border rounded shadow"
      />
    ) : (
      <div className="text-gray-500 italic">No visual available.</div>
    )}
    {description && (
      <div className="mt-2 text-sm text-gray-600">{description}</div>
    )}
  </div>
);

export default VisualOutput;
