import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { Source, SourceType, TaxonomySource } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { SourceBadgeText } from "../source-badge-text";
import { cn } from "@/lib/utils";
import { ParagraphSource } from "../paragraph-sources";

interface TaxonomyProps {
  taxonomyTerms: TaxonomySource[];
  onSourceSelect?: (source: Source) => void;
}

export const Taxonomy = ({ taxonomyTerms, onSourceSelect }: TaxonomyProps) => {
  const {
    filter,
    searchQuery,
    hoveredSourceId,
    setHoveredSourceId,
    selectSource,
  } = useSidebarStore();
  const isFiltered = filter === SourceType.TAXONOMY || filter === "all";

  // also reduce to single term per label
  const filteredTaxonomyTerms = taxonomyTerms
    .filter((term) =>
      term.value.label.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .reduce<typeof taxonomyTerms>((acc, term) => {
      if (!acc.some((t) => t.value.label === term.value.label)) {
        acc.push(term);
      }
      return acc;
    }, []);

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
        filteredTaxonomyTerms.map((term, index) => {
          const isHovered = hoveredSourceId === term.value.context[0]?.id;
          return (
            <SidebarMenuItem
              key={`term-${index}`}
              className={cn(
                "mb-2 border p-4 overflow-hidden transition-all duration-200 cursor-pointer",
                isHovered && "bg-white shadow-md"
              )}
              onClick={() => handleSourceSelect(term)}
              onMouseEnter={() =>
                term.value.context[0]?.id &&
                setHoveredSourceId(term.value.context[0]?.id)
              }
              onMouseLeave={() => setHoveredSourceId(null)}
            >
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">
                      {term.value.label}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* <ParagraphSource id={term.value.context[0].id} isNoHover /> */}
                  <SourceBadgeText sourceType={SourceType.TAXONOMY} />
                </div>
              </div>
            </SidebarMenuItem>
          );
        })}
    </>
  );
};
