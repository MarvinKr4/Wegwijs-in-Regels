import { SourceType } from "@/lib/types";
import React from "react";
import { Button } from "./ui/button";
import { useSidebarStore } from "@/store/sidebar-store";
import { cn } from "@/lib/utils";

export const Filters = () => {
  const {
    usedSourceCount,
    lawArticles,
    caseLawSources,
    taxonomySources,
    selectielijstSources,
    werkinstructieSources,
    allLawArticles,
    allCaseLawSources,
    allTaxonomySources,
    allSelectielijstSources,
    allWerkinstructieSources,
    filter,
    setFilter,
    showAllSources,
  } = useSidebarStore();

  // Calculate unused source counts
  const unusedLawArticles = allLawArticles.filter(
    (article) => !lawArticles.some((used) => used.id === article.id)
  );
  const unusedCaseLawSources = allCaseLawSources.filter(
    (source) => !caseLawSources.some((used) => used.id === source.id)
  );
  const unusedTaxonomySources = allTaxonomySources.filter(
    (source) => !taxonomySources.some((used) => used.id === source.id)
  );
  const unusedSelectielijstSources = allSelectielijstSources.filter(
    (source) => !selectielijstSources.some((used) => used.id === source.id)
  );
  const unusedWerkinstructieSources = allWerkinstructieSources.filter(
    (source) => !werkinstructieSources.some((used) => used.id === source.id)
  );

  const unusedSourceCount =
    unusedLawArticles.length +
    unusedCaseLawSources.length +
    unusedTaxonomySources.length +
    unusedSelectielijstSources.length +
    unusedWerkinstructieSources.length;

  const filters = [
    {
      id: "all",
      name: "Alles",
      count: showAllSources ? unusedSourceCount : usedSourceCount,
    },
    {
      id: SourceType.LAW,
      name: "Wetten",
      count: showAllSources ? unusedLawArticles.length : lawArticles.length,
    },
    {
      id: SourceType.CASE_LAW,
      name: "Jurisprudentie",
      count: showAllSources
        ? unusedCaseLawSources.length
        : caseLawSources.length,
    },
    {
      id: SourceType.TAXONOMY,
      name: "Taxonomie",
      count: showAllSources
        ? unusedTaxonomySources.length
        : taxonomySources.length,
    },
    {
      id: SourceType.SELECTIELIJST,
      name: "Selectielijst",
      count: showAllSources
        ? unusedSelectielijstSources.length
        : selectielijstSources.length,
    },
    {
      id: SourceType.WERKINSTRUCTIE,
      name: "Werkinstructie",
      count: showAllSources
        ? unusedWerkinstructieSources.length
        : werkinstructieSources.length,
    },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {filters.map((f) => (
        <Button
          key={f.id}
          variant="outline"
          size="sm"
          onClick={() =>
            setFilter(f.id === "all" ? "all" : (f.id as SourceType))
          }
          className={cn(
            "text-xs rounded-full border-2 px-4 py-5 ",
            filter === f.id && "border-lichtblauw"
          )}
        >
          {f.name} {f.count !== null && `(${f.count})`}
        </Button>
      ))}
    </div>
  );
};
