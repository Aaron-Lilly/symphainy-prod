import React from "react";

interface ErrorMessageProps {
  message: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => (
  <div className="bg-red-100 text-red-700 p-2 rounded mb-2">
    {message || "Unknown error."}
  </div>
);

export default ErrorMessage;
