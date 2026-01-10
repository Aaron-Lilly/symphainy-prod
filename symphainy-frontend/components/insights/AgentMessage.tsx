import React from "react";

interface AgentMessageProps {
  content: string;
}

const AgentMessage: React.FC<AgentMessageProps> = ({ content }) => (
  <div className="bg-blue-50 text-blue-900 p-3 rounded mb-2 border border-blue-200">
    {content}
  </div>
);

export default AgentMessage;
