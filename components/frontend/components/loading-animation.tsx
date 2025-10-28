import React from "react";

export const LoadingAnimation = () => {
  return (
    <div className="mb-4 p-3 rounded-lg bg-white text-black ml-auto max-w-[80%]">
      <div className="flex items-center">
        <div className="ml-2 flex space-x-1">
          <div
            className="h-2 w-2 rounded-full bg-lintblauw animate-bounce"
            style={{ animationDelay: "0ms" }}
          ></div>
          <div
            className="h-2 w-2 rounded-full bg-lintblauw animate-bounce"
            style={{ animationDelay: "150ms" }}
          ></div>
          <div
            className="h-2 w-2 rounded-full bg-lintblauw animate-bounce"
            style={{ animationDelay: "300ms" }}
          ></div>
        </div>
      </div>
    </div>
  );
};
