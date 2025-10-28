"use client";

import { useSidebarStore } from "@/store/sidebar-store";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ArrowDownUp, Search } from "lucide-react"; // Make sure you have lucide-react installed
import { SidebarContent } from "./sidebar-content";
import { Input } from "./ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SourceDetail } from "./source-detail";
import { useRef, useEffect } from "react";
import { Filters } from "./filters";
import { UnusedSourcesDialog } from "./unused-sources-dialog";

export function SourcesSidebar() {
  const sidebarRef = useRef<HTMLDivElement>(null);

  const {
    isOpen,
    searchQuery,
    setSearchQuery,
    selectedSource,
    selectSource,
    showAllSources,
    setShowAllSources,
  } = useSidebarStore();

  // Add effect to scroll to top when a source is selected
  useEffect(() => {
    if (selectedSource && sidebarRef.current) {
      sidebarRef.current.scrollTop = 0;
    }
  }, [selectedSource]);

  return (
    <div
      ref={sidebarRef}
      className={cn(
        "bg-gray-100 shadow-lg transition-all duration-300 ease-in-out border-l h-full overflow-y-auto",
        isOpen ? "w-[40%]" : "w-0 opacity-0 overflow-hidden"
      )}
    >
      <div className="flex flex-col h-full">
        {selectedSource ? (
          <SourceDetail
            source={selectedSource}
            onBack={() => {
              if (sidebarRef.current) {
                sidebarRef.current.scrollTop = 0;
              }
              selectSource(null);
            }}
          />
        ) : (
          <>
            <div className="border-b p-4 pt-10">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold mb-4">Bronnen</h2>
                <UnusedSourcesDialog />
              </div>
              {/* Search bar */}
              <div className="flex w-full items-center mb-4 gap-2">
                <div className="relative w-full">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    className="w-full pl-10 pr-3 py-5 border rounded-full bg-white focus-visible:border-lichtblauw focus-visible:ring-lichtblauw focus-visible:ring-[2px]"
                    placeholder="Bronnen doorzoeken"
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                    }}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        className="rounded-full px-4 py-5"
                      >
                        <ArrowDownUp className="size-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Optie A</DropdownMenuItem>
                      <DropdownMenuItem>Optie B</DropdownMenuItem>
                      <DropdownMenuItem>Optie C</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              {/* Filter buttons */}
              <Filters />
            </div>

            {/* Sources content */}
            <SidebarContent />
          </>
        )}
      </div>
    </div>
  );
}
