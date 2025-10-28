import React from "react";
import { Badge } from "./ui/badge";
import { SourceType, SourceTypeLabel } from "@/lib/types";
import { cn, getTailwindClasses } from "@/lib/utils";

export const SourceBadgeText = ({ sourceType }: { sourceType: SourceType }) => {
  return (
    <Badge
      variant="outline"
      className={cn(
        getTailwindClasses(sourceType),
        "rounded-full py-1 px-3 text-xs font-medium"
      )}
    >
      {
        SourceTypeLabel[
          sourceType.toUpperCase() as keyof typeof SourceTypeLabel
        ]
      }
    </Badge>
  );
};
