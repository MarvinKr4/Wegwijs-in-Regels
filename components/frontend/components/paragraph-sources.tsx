import React from "react";
import { SourceType, TaxonomySource } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { getTailwindClasses } from "@/lib/utils";
import { cn } from "@/lib/utils";

export const ParagraphSource = ({
  id,
  isNoHover,
}: {
  id?: string;
  isNoHover?: boolean;
}) => {
  const { legalData, hoveredSourceId, setHoveredSourceId, selectSource } =
    useSidebarStore();

  if (!id) return null;

  // First try to find the source directly
  let source = legalData?.answer.sources.find((source) => source.id === id);

  // If not found and it's a taxonomy source, look in the context array
  if (!source && id.startsWith("source_")) {
    const taxonomySource = legalData?.answer.sources.find(
      (s): s is TaxonomySource =>
        s.type === SourceType.TAXONOMY &&
        s.value.context.some((c) => c.id === id)
    );

    if (taxonomySource) {
      const contextItem = taxonomySource.value.context.find((c) => c.id === id);
      if (contextItem) {
        source = {
          id,
          type: SourceType.TAXONOMY,
          value: {
            label: taxonomySource.value.label,
            context: [contextItem],
          },
        };
      }
    }
  }

  if (!source) return null;

  const isHovered = hoveredSourceId === id;
  const tailwindClasses = getTailwindClasses(source.type);
  // Extract the border color from the tailwind classes
  const borderColor =
    tailwindClasses
      .split(" ")
      .find((cls) => cls.startsWith("border-"))
      ?.replace("border-", "bg-") || "bg-gray-500";

  return (
    <div className="">
      <div
        onClick={() => selectSource(source)}
        className={cn(
          tailwindClasses,
          "size-6 place-content-center grid rounded-md cursor-pointer bg-transparent border-2 text-xs font-medium text-black transition-all duration-200",
          isHovered && cn("scale-110", borderColor, "text-white")
        )}
        key={id}
        onMouseEnter={() => !isNoHover && setHoveredSourceId(id)}
        onMouseLeave={() => !isNoHover && setHoveredSourceId(null)}
      >
        {id?.split("_")[1]}
      </div>
    </div>
  );
};
