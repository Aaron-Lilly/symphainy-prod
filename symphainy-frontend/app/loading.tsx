import { Loader } from "@/components/ui/loader";
import React from "react";

export default function Loading() {
  return (
    <>
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h1 className="text-h1 text-2xl text-gradient-to-r from-blue-600 to-purple-600 font-bold mb-4">
            Welcome back!
          </h1>
          <div className="flex items-center justify-center">
            <Loader size="xl" className="text-purple-500" />
          </div>
        </div>
      </div>
    </>
  );
}
