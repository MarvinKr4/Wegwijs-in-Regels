import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { CaseLawSource, Source, SourceType } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { SourceBadgeText } from "../source-badge-text";
import { ParagraphSource } from "../paragraph-sources";
import { cn } from "@/lib/utils";

interface CaseLawProps {
  caseLawSources: CaseLawSource[];
  onSourceSelect?: (source: Source) => void;
}

export const CaseLaw = ({ caseLawSources, onSourceSelect }: CaseLawProps) => {
  const {
    filter,
    searchQuery,
    hoveredSourceId,
    setHoveredSourceId,
    selectSource,
  } = useSidebarStore();
  const isFiltered = filter === SourceType.CASE_LAW || filter === "all";
  const filteredCaseLawSources = caseLawSources.filter(
    (source) =>
      source.value.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (source.value.document &&
        source.value.document.toLowerCase().includes(searchQuery.toLowerCase()))
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
        filteredCaseLawSources.map((source, index) => {
          const isHovered = hoveredSourceId === source.id;
          return (
            <SidebarMenuItem
              key={`case-law-${index}`}
              className={cn(
                "mb-2 border p-4 overflow-hidden transition-all duration-200 cursor-pointer",
                isHovered && "bg-white shadow-md"
              )}
              onMouseEnter={() => source.id && setHoveredSourceId(source.id)}
              onMouseLeave={() => setHoveredSourceId(null)}
              onClick={() => handleSourceSelect(source)}
            >
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">
                      {source.value.title}
                    </div>
                    {source.value.document && (
                      <div className="text-sm text-muted-foreground line-clamp-2">
                        {source.value.document}
                      </div>
                    )}
                  </div>
                  {source.value.url && (
                    <a
                      href={source.value.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground mr-2 shrink-0"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Link
                    </a>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <ParagraphSource id={source.id} isNoHover />
                  <SourceBadgeText sourceType={SourceType.CASE_LAW} />
                </div>
              </div>
            </SidebarMenuItem>
          );
        })}
    </>
  );
};

export default CaseLaw;
