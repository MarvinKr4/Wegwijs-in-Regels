"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ArrowDownUp, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useSidebarStore } from "@/store/sidebar-store";
import { SidebarContent } from "./sidebar-content";
import { Filters } from "./filters";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Source } from "@/lib/types";
import { SourceDetail } from "./source-detail";

export function UnusedSourcesDialog() {
  const { searchQuery, setSearchQuery, showAllSources, setShowAllSources } =
    useSidebarStore();
  const [open, setOpen] = React.useState(false);
  const [selectedSource, setSelectedSource] = React.useState<Source | null>(
    null
  );

  return (
    <Dialog
      open={open}
      onOpenChange={(isOpen) => {
        setOpen(isOpen);
        if (isOpen) {
          setShowAllSources(true);
          setSelectedSource(null);
        } else {
          setShowAllSources(false);
        }
      }}
    >
      <DialogTrigger asChild>
        <Button
          variant="link"
          className="text-xs text-hemelblauw cursor-pointer"
        >
          Ongebruikte bronnen
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-[800px] h-[80vh] p-0 bg-gray-100">
        {selectedSource ? (
          <SourceDetail
            source={selectedSource}
            onBack={() => setSelectedSource(null)}
          />
        ) : (
          <>
            <DialogHeader className="p-4 border-b bg-white">
              <div className="flex justify-between items-center">
                <DialogTitle className="text-xl font-semibold mb-4">
                  Ongebruikte bronnen
                </DialogTitle>
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
                    <DropdownMenuContent>
                      <DropdownMenuItem>Optie A</DropdownMenuItem>
                      <DropdownMenuItem>Optie B</DropdownMenuItem>
                      <DropdownMenuItem>Optie C</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              {/* Filter buttons */}
              <Filters />
            </DialogHeader>

            <div className="overflow-y-auto h-[calc(80vh-200px)] bg-white">
              <SidebarContent onSourceSelect={setSelectedSource} />
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
