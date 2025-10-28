"use client";
import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { Source, SourceType, WerkinstructieSource } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { SourceBadgeText } from "../source-badge-text";
import { ParagraphSource } from "../paragraph-sources";
import { cn } from "@/lib/utils";

interface WerkinstructieProps {
  werkinstructies: WerkinstructieSource[];
  onSourceSelect?: (source: Source) => void;
}

export const Werkinstructie = ({
  werkinstructies,
  onSourceSelect,
}: WerkinstructieProps) => {
  const {
    filter,
    searchQuery,
    hoveredSourceId,
    setHoveredSourceId,
    selectSource,
  } = useSidebarStore();

  const isFiltered = filter === SourceType.WERKINSTRUCTIE || filter === "all";

  const filteredWerkinstructies = werkinstructies.filter(
    (w) =>
      w.value.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.value.chunks.some((chunk) =>
        chunk.toLowerCase().includes(searchQuery.toLowerCase())
      )
  );

  const handleSourceSelect = (source: Source) => {
    if (onSourceSelect) {
      onSourceSelect(source);
    } else {
      selectSource(source);
    }
  };

  return (
    <>
      {isFiltered &&
        filteredWerkinstructies.map((werkinstructie, index) => {
          const isHovered = hoveredSourceId === werkinstructie.id;
          return (
            <SidebarMenuItem
              key={`werkinstructie-${index}`}
              className={cn(
                "mb-2 border p-4 overflow-hidden transition-all duration-200 cursor-pointer",
                isHovered && "bg-white shadow-md"
              )}
              onMouseEnter={() =>
                werkinstructie.id && setHoveredSourceId(werkinstructie.id)
              }
              onMouseLeave={() => setHoveredSourceId(null)}
              onClick={() => handleSourceSelect(werkinstructie)}
            >
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">
                      {werkinstructie.value.title}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <ParagraphSource id={werkinstructie.id} isNoHover />
                  <SourceBadgeText sourceType={SourceType.WERKINSTRUCTIE} />
                </div>
              </div>
            </SidebarMenuItem>
          );
        })}
    </>
  );
};
