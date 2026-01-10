import React from "react";

interface SummaryOutputProps {
  summary: string;
}

const SummaryOutput: React.FC<SummaryOutputProps> = ({ summary }) => (
  <div
    className="prose max-w-none"
    dangerouslySetInnerHTML={{ __html: summary }}
  />
);

export default SummaryOutput;
