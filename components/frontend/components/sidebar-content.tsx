"use client";

import React from "react";
import { useSidebarStore } from "@/store/sidebar-store";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
} from "@/components/ui/sidebar";
import { SidebarSourcesSkeleton } from "@/components/skeleton-loaders/sidebar-sources-skeleton";
import { LawArticles } from "./sources/law-articles";
import { Taxonomy } from "./sources/taxonomy";
import { Selectielijst } from "./sources/selectielijst";
import { CaseLaw } from "./sources/case-law";
import FileUpload from "./ui/file-upload";
import { Werkinstructie } from "./sources/werkinstructie";
import { Source } from "@/lib/types";

interface SidebarContentProps {
  onSourceSelect?: (source: Source) => void;
}

export const SidebarContent = ({ onSourceSelect }: SidebarContentProps) => {
  const {
    lawArticles,
    caseLawSources,
    taxonomySources,
    selectielijstSources,
    isEmpty,
    werkinstructieSources,
    allLawArticles,
    allCaseLawSources,
    allTaxonomySources,
    allSelectielijstSources,
    allWerkinstructieSources,
    showAllSources,
  } = useSidebarStore();

  // Filter out used sources from all sources to get unused sources
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

  const sources = showAllSources
    ? {
        lawArticles: allLawArticles,
        caseLawSources: allCaseLawSources,
        taxonomySources: allTaxonomySources,
        selectielijstSources: allSelectielijstSources,
        werkinstructieSources: allWerkinstructieSources,
      }
    : {
        lawArticles,
        caseLawSources,
        taxonomySources,
        selectielijstSources,
        werkinstructieSources,
      };

  return (
    <SidebarGroup>
      {/* <FileUpload /> */}
      <SidebarGroupContent>
        <SidebarMenu>
          {isEmpty ? (
            <SidebarSourcesSkeleton />
          ) : !showAllSources ? (
            <>
              <LawArticles
                lawArticles={sources.lawArticles}
                onSourceSelect={onSourceSelect}
              />
              <CaseLaw
                caseLawSources={sources.caseLawSources}
                onSourceSelect={onSourceSelect}
              />
              <Taxonomy
                taxonomyTerms={sources.taxonomySources}
                onSourceSelect={onSourceSelect}
              />
              <Selectielijst
                selectielijstRows={sources.selectielijstSources}
                onSourceSelect={onSourceSelect}
              />
              <Werkinstructie
                werkinstructies={sources.werkinstructieSources}
                onSourceSelect={onSourceSelect}
              />
            </>
          ) : (
            <>
              <LawArticles
                lawArticles={unusedLawArticles}
                onSourceSelect={onSourceSelect}
              />
              <CaseLaw
                caseLawSources={unusedCaseLawSources}
                onSourceSelect={onSourceSelect}
              />
              <Taxonomy
                taxonomyTerms={unusedTaxonomySources}
                onSourceSelect={onSourceSelect}
              />
              <Selectielijst
                selectielijstRows={unusedSelectielijstSources}
                onSourceSelect={onSourceSelect}
              />
              <Werkinstructie
                werkinstructies={unusedWerkinstructieSources}
                onSourceSelect={onSourceSelect}
              />
            </>
          )}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
};
