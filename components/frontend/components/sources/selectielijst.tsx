import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { SelectielijstSource, Source, SourceType } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { SourceBadgeText } from "../source-badge-text";
import { ParagraphSource } from "../paragraph-sources";
import { cn } from "@/lib/utils";

interface SelectielijstProps {
  selectielijstRows: SelectielijstSource[];
  onSourceSelect?: (source: Source) => void;
}

export const Selectielijst = ({
  selectielijstRows,
  onSourceSelect,
}: SelectielijstProps) => {
  const {
    filter,
    searchQuery,
    hoveredSourceId,
    setHoveredSourceId,
    selectSource,
  } = useSidebarStore();
  const isFiltered = filter === SourceType.SELECTIELIJST || filter === "all";

  const filteredSelectielijstRows = selectielijstRows.filter(
    (row) =>
      row.value?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      row.value?.rows?.some((row) =>
        row.omschrijving.toLowerCase().includes(searchQuery.toLowerCase())
      ) ||
      row.value?.rows?.some((row) =>
        row.voorbeeldstukken.toLowerCase().includes(searchQuery.toLowerCase())
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
        filteredSelectielijstRows.map((row, index) => {
          const isHovered = hoveredSourceId === row.id;
          return (
            <SidebarMenuItem
              key={`selectielijst-${index}`}
              className={cn(
                "mb-2 border p-4 overflow-hidden transition-all duration-200 cursor-pointer",
                isHovered && "bg-white shadow-md"
              )}
              onMouseEnter={() => row.id && setHoveredSourceId(row.id)}
              onMouseLeave={() => setHoveredSourceId(null)}
              onClick={() => handleSourceSelect(row)}
            >
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">
                      {row.value.name.charAt(0).toUpperCase() +
                        row.value.name.slice(1)}
                    </div>
                    {row.value.rows && row.value.rows.length > 0 && (
                      <div className="text-sm text-muted-foreground line-clamp-2">
                        {row.value.rows[0].omschrijving}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <ParagraphSource id={row.id} isNoHover />
                  <SourceBadgeText sourceType={SourceType.SELECTIELIJST} />
                </div>
              </div>
            </SidebarMenuItem>
          );
        })}
    </>
  );
};
