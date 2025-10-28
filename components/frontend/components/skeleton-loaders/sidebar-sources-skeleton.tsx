import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { Skeleton } from "../ui/skeleton";

export const SidebarSourcesSkeleton = () => {
  return (
    <>
      {/* Generic Item Skeletons */}
      {[1, 2, 3, 4, 5].map((_, index) => (
        <SidebarMenuItem
          key={`skeleton-${index}`}
          className="mb-2 border p-4 overflow-hidden"
        >
          <div className="flex items-start gap-2 w-full">
            <Skeleton className="h-6 w-24 rounded-md shrink-0" />{" "}
            {/* Badge skeleton */}
            <div className="flex-1 min-w-0">
              <Skeleton className="h-5 w-3/4 mb-2" />
              <Skeleton className="h-4 w-full mb-1" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            <Skeleton className="h-5 w-5 mr-2 shrink-0" />{" "}
            {/* Number skeleton */}
          </div>
        </SidebarMenuItem>
      ))}
    </>
  );
};
