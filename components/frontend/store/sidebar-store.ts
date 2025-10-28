import { create } from "zustand";
import {
  LegalData,
  LawSource,
  CaseLawSource,
  TaxonomySource,
  SelectielijstSource,
  SourceType,
  WerkinstructieSource,
  Source,
} from "@/lib/types";

interface SidebarState {
  isOpen: boolean;
  legalData: LegalData | null;
  filter: SourceType | "all";
  searchQuery: string;
  showAllSources: boolean;

  // Helper properties for quickly accessing specific source types
  lawArticles: LawSource[];
  caseLawSources: CaseLawSource[];
  taxonomySources: TaxonomySource[];
  selectielijstSources: SelectielijstSource[];
  werkinstructieSources: WerkinstructieSource[];

  allLawArticles: LawSource[];
  allCaseLawSources: CaseLawSource[];
  allTaxonomySources: TaxonomySource[];
  allSelectielijstSources: SelectielijstSource[];
  allWerkinstructieSources: WerkinstructieSource[];

  // Added isEmpty property
  isEmpty: boolean;
  // Total number of items across all sources
  totalItems: number;
  usedSourceCount: number;
  // Source selection state
  selectedSource: Source | null;

  // UI actions
  openSidebar: () => void;
  closeSidebar: () => void;
  toggleSidebar: () => void;
  setSearchQuery: (query: string) => void;
  // Data actions
  setLegalData: (data: LegalData) => void;
  setAllSources: (sources: LegalData) => void;
  clearLegalData: () => void;
  setFilter: (filter: SourceType | "all") => void;
  // Source selection actions
  selectSource: (source: Source | null) => void;
  setShowAllSources: (show: boolean) => void;
}

interface SidebarStore extends SidebarState {
  hoveredSourceId: string | null;
  setHoveredSourceId: (id: string | null) => void;
}

export const useSidebarStore = create<SidebarStore>((set, get) => ({
  isOpen: false,
  filter: "all",
  searchQuery: "",
  // Initialize typed sources
  legalData: null,
  lawArticles: [],
  caseLawSources: [],
  taxonomySources: [],
  selectielijstSources: [],
  werkinstructieSources: [],

  allLawArticles: [],
  allCaseLawSources: [],
  allTaxonomySources: [],
  allSelectielijstSources: [],
  allWerkinstructieSources: [],

  isEmpty: true,
  totalItems: 0,
  usedSourceCount: 0,
  hoveredSourceId: null,
  selectedSource: null,
  showAllSources: false,
  // UI actions
  setFilter: (filter: SourceType | "all") => set({ filter }),
  setSearchQuery: (query: string) => set({ searchQuery: query }),
  openSidebar: () => set({ isOpen: true }),
  closeSidebar: () => set({ isOpen: false }),
  toggleSidebar: () => set((state) => ({ isOpen: !state.isOpen })),

  // Source selection actions
  selectSource: (source) => set({ selectedSource: source }),

  setAllSources: (sources: LegalData) => {
    set({
      allLawArticles: sources.answer.sources.filter(
        (source): source is LawSource => source.type === SourceType.LAW
      ),
      allCaseLawSources: sources.answer.sources.filter(
        (source): source is CaseLawSource => source.type === SourceType.CASE_LAW
      ),
      allTaxonomySources: sources.answer.sources.filter(
        (source): source is TaxonomySource =>
          source.type === SourceType.TAXONOMY
      ),
      allSelectielijstSources: sources.answer.sources.filter(
        (source): source is SelectielijstSource =>
          source.type === SourceType.SELECTIELIJST
      ),
      allWerkinstructieSources: sources.answer.sources.filter(
        (source): source is WerkinstructieSource =>
          source.type === SourceType.WERKINSTRUCTIE
      ),
    });
  },

  // Data actions
  setLegalData: (data: LegalData) => {
    const sources = data?.answer.sources || [];

    const lawArticles = sources
      .filter((source): source is LawSource => source.type === SourceType.LAW)
      .filter((source) => source.value.isSource);

    const caseLawSources = sources.filter((source): source is CaseLawSource => {
      if (source.type !== SourceType.CASE_LAW) return false;
      // Filter alleen de bronnen met isSource: true
      return source.value.isSource;
    });

    const taxonomySources = sources.filter(
      (source): source is TaxonomySource => {
        if (source.type !== SourceType.TAXONOMY) return false;
        // Filter alleen de context items met isSource: true
        source.value.context = source.value.context.filter(
          (context) => context.isSource
        );
        // Alleen bronnen behouden die nog context items over hebben
        return source.value.context.length > 0;
      }
    );

    const selectielijstSources = sources.filter(
      (source): source is SelectielijstSource => {
        if (source.type !== SourceType.SELECTIELIJST) return false;
        // Filter rows to only include those with isSource: true
        source.value.rows = source.value.rows.filter((row) => row.isSource);
        // Only keep sources that still have rows after filtering
        return source.value.rows.length > 0;
      }
    );

    const werkinstructieSources = sources
      .filter((source): source is WerkinstructieSource => {
        if (source.type !== SourceType.WERKINSTRUCTIE) return false;
        // Filter alleen de bronnen met isSource: true
        return source.value.isSource;
      })
      .filter((source) => source.value.isSource);

    const totalItems = sources.length;
    const usedSourceCount =
      selectielijstSources.length +
      caseLawSources.length +
      lawArticles.length +
      taxonomySources.length;

    const isEmpty = usedSourceCount === 0;

    set({
      legalData: data,
      lawArticles,
      caseLawSources,
      taxonomySources,
      selectielijstSources,
      werkinstructieSources,
      isEmpty,
      totalItems,
      usedSourceCount,
      isOpen: true,
    });
  },

  clearLegalData: () =>
    set({
      legalData: null,
      lawArticles: [],
      caseLawSources: [],
      taxonomySources: [],
      selectielijstSources: [],
      werkinstructieSources: [],
      isEmpty: true, // Reset to true when clearing data
      totalItems: 0, // Reset total count to 0
      selectedSource: null,
    }),

  setHoveredSourceId: (id) => set({ hoveredSourceId: id }),
  setShowAllSources: (show: boolean) => set({ showAllSources: show }),
}));
