import { Loader2 } from "lucide-react";
import React from "react";

export default function Loading() {
  return (
    <div className="flex pb-32 items-center justify-center h-screen">
      <div className="text-center flex justify-center items-center">
        <Loader2 className="w-10 h-10 animate-spin" />
      </div>
    </div>
  );
}
