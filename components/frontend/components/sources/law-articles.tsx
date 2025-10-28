import React from "react";
import { SidebarMenuItem } from "../ui/sidebar";
import { LawSource, Source, SourceType } from "@/lib/types";
import { useSidebarStore } from "@/store/sidebar-store";
import { SourceBadgeText } from "../source-badge-text";
import { ParagraphSource } from "../paragraph-sources";
import { cn } from "@/lib/utils";

interface LawArticlesProps {
  lawArticles: LawSource[];
  onSourceSelect?: (source: Source) => void;
}

export const LawArticles = ({
  lawArticles,
  onSourceSelect,
}: LawArticlesProps) => {
  const {
    filter,
    searchQuery,
    hoveredSourceId,
    setHoveredSourceId,
    selectSource,
  } = useSidebarStore();
  const isFiltered = filter === SourceType.LAW || filter === "all";
  const filteredLawArticles = lawArticles.filter(
    (article) =>
      article.value.law.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.value.title.toLowerCase().includes(searchQuery.toLowerCase())
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
        filteredLawArticles.map((article, index) => {
          const isHovered = hoveredSourceId === article.id;
          return (
            <SidebarMenuItem
              key={`law-${index}`}
              className={cn(
                "mb-2 border p-4 overflow-hidden transition-all duration-200 cursor-pointer",
                isHovered && "bg-white shadow-md"
              )}
              onMouseEnter={() => article.id && setHoveredSourceId(article.id)}
              onMouseLeave={() => setHoveredSourceId(null)}
              onClick={() => handleSourceSelect(article)}
            >
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">
                      {article.value.law}
                    </div>
                    <div className="text-sm text-muted-foreground line-clamp-2">
                      {article.value.title}
                    </div>
                  </div>
                  {article.value.url && (
                    <a
                      href={article.value.url}
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
                  <ParagraphSource id={article.id} isNoHover />
                  <SourceBadgeText sourceType={SourceType.LAW} />
                </div>
              </div>
            </SidebarMenuItem>
          );
        })}
    </>
  );
};

export default LawArticles;
