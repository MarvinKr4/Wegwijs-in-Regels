import React, { useState, useEffect, useRef, CSSProperties } from "react";
import ReactMarkdown from "react-markdown";
import { SourceType, TextParagraph } from "@/lib/types";
import { ParagraphSource } from "./paragraph-sources";
import { useSidebarStore } from "@/store/sidebar-store";
import { cn, getTailwindClasses } from "@/lib/utils";
import { Button } from "./ui/button";

interface MarkdownRendererProps {
  content: TextParagraph[] | string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
}) => {
  const { hoveredSourceId, setHoveredSourceId, taxonomySources } =
    useSidebarStore();
  const [expandedParagraphs, setExpandedParagraphs] = useState<Set<number>>(
    new Set()
  );
  const [clickedSourceId, setClickedSourceId] = useState<string | null>(null);
  const markdownRef = useRef<HTMLDivElement>(null);

  const getDefinitionByTaxonomyId = (id: string) => {
    const source = taxonomySources.find((source) =>
      source.value.context.find((ctx) => ctx.id === id)
    );
    return source?.value.context[0].definition;
  };

  const toggleParagraphExpansion = (paragraphIndex: number) => {
    setExpandedParagraphs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(paragraphIndex)) {
        newSet.delete(paragraphIndex);
      } else {
        newSet.add(paragraphIndex);
      }
      return newSet;
    });
  };

  // Set up global mouse move listener for the markdown container
  useEffect(() => {
    // Keep track of the current hovered source ID to prevent unnecessary updates
    let currentHoveredId: string | null = null;

    const handleMouseMove = (e: MouseEvent) => {
      // Find all elements under the cursor
      const elements = document.elementsFromPoint(e.clientX, e.clientY);

      // Check if any of these elements have a source ID
      const sourceElement = elements.find(
        (el) => el.id && el.id.startsWith("source-")
      );

      if (sourceElement) {
        // Extract source ID from the element ID
        const sourceId = sourceElement.id.replace("source-", "");

        // Only update if it's different from the current hovered ID
        if (sourceId !== currentHoveredId) {
          currentHoveredId = sourceId;
          setHoveredSourceId(sourceId);
        }
      } else if (
        currentHoveredId !== null &&
        markdownRef.current?.contains(e.target as Node)
      ) {
        // Reset only if we actually have a current ID and we're still in the markdown container
        currentHoveredId = null;
        setHoveredSourceId(null);
      }
    };

    // Throttle the mouse move handler to reduce updates
    const throttledHandleMouseMove = throttle(handleMouseMove, 50);

    // Add global mouse move listener
    document.addEventListener("mousemove", throttledHandleMouseMove);

    // Cleanup
    return () => {
      document.removeEventListener("mousemove", throttledHandleMouseMove);
    };
  }, [setHoveredSourceId]);

  // Add this effect to handle clicks outside sources
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (clickedSourceId) {
        const elements = document.elementsFromPoint(e.clientX, e.clientY);
        const isClickedInsideSource = elements.some(
          (el) => el.id && el.id.startsWith("source-")
        );

        if (!isClickedInsideSource) {
          setClickedSourceId(null);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [clickedSourceId]);

  // Function to handle source clicks
  const handleSourceClick = (sourceId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setClickedSourceId(clickedSourceId === sourceId ? null : sourceId);
  };

  // return a css style object for the tooltip
  const getTooltipTransform = (element: HTMLElement): CSSProperties => {
    // Get the clicked element's position
    const sourceRect = element.getBoundingClientRect();

    // Get the markdown container bounds
    const markdownContainer = markdownRef.current;
    if (!markdownContainer) return { top: "100%", left: "-50%" };

    const containerRect = markdownContainer.getBoundingClientRect();

    // Calculate the element's position relative to the container
    const relativeLeft = sourceRect.left - containerRect.left;

    // Assume tooltip dimensions
    const TOOLTIP_WIDTH = 400; // min-w-[400px]
    const BUFFER = 20;

    let position: CSSProperties = {
      top: "100%", // Altijd onder het element
      left: "-50%", // Standaard gecentreerd
    };

    // Bereken of de tooltip rechts buiten de container zou vallen
    console.log("relative", relativeLeft);

    const tooltipRight = relativeLeft + TOOLTIP_WIDTH / 1.3;
    console.log(tooltipRight);

    if (tooltipRight > containerRect.width - BUFFER) {
      // Bereken hoeveel we moeten compenseren
      const overflow = tooltipRight - (containerRect.width - BUFFER);
      position.transform = `translateX(-${overflow}px)`;
    }

    // Check ook voor links overflow
    const tooltipLeft = relativeLeft - TOOLTIP_WIDTH / 2;
    if (tooltipLeft < BUFFER) {
      // Als de tooltip te ver naar links zou gaan, corrigeer dit
      position.transform = `translateX(${Math.abs(tooltipLeft) + BUFFER}px)`;
    }

    return position;
  };

  if (Array.isArray(content)) {
    return (
      <div
        ref={markdownRef}
        className="markdown-content prose prose-neutral max-w-none"
      >
        {content.map((item, paragraphIndex) => {
          // Houd een teller bij voor woorden binnen deze paragraaf
          let wordCounter = 0;

          const processedParagraph = item.paragraph.replace(
            /([\w-]+)<source_(\d+)>/g,
            (_, word, sourceId) => `[${word}](#source_${sourceId})`
          );

          return (
            <div key={paragraphIndex} className="mb-4">
              <ReactMarkdown
                components={{
                  a: ({ href, children }) => {
                    if (href?.startsWith("#source_")) {
                      const sourceId = href.replace("#", "");
                      const isHovered = hoveredSourceId === sourceId;
                      const id = `source-${sourceId}-p${paragraphIndex}-w${wordCounter++}`;
                      return (
                        <span id={id} className="relative inline-block">
                          <span
                            className={cn(
                              "cursor-pointer transition-all duration-200 px-1 rounded",
                              isHovered
                                ? "bg-yellow-200/80"
                                : "bg-yellow-200/30"
                            )}
                            onClick={(e) => handleSourceClick(id, e)}
                          >
                            {children}
                          </span>

                          {clickedSourceId === id && (
                            <span
                              style={getTooltipTransform(
                                document.getElementById(id) as HTMLElement
                              )}
                              className={cn(
                                "absolute h-fit mt-1 !bg-white shadow-lg p-4 z-50 min-w-[400px]",
                                "rounded-xl"
                              )}
                            >
                              <span className="relative block w-full h-full pl-4">
                                <span
                                  className={cn(
                                    "absolute w-2 left-0 top-0 bottom-0 ",
                                    getTailwindClasses(SourceType.TAXONOMY)
                                  )}
                                ></span>
                                <span className="block py-2">
                                  {getDefinitionByTaxonomyId(sourceId)}
                                </span>
                              </span>
                            </span>
                          )}
                        </span>
                      );
                    }
                    return <a href={href}>{children}</a>;
                  },
                }}
              >
                {processedParagraph}
              </ReactMarkdown>
              {item.sources.length < 5 ||
              expandedParagraphs.has(paragraphIndex) ? (
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <div className="flex gap-2">
                    {item.sources.map((sourceId) => (
                      <ParagraphSource key={sourceId} id={sourceId} />
                    ))}
                  </div>
                  {expandedParagraphs.has(paragraphIndex) && (
                    <Button
                      variant="secondary"
                      onClick={() => toggleParagraphExpansion(paragraphIndex)}
                      className="w-fit"
                    >
                      Bronnen verbergen
                    </Button>
                  )}
                </div>
              ) : (
                <Button
                  variant="secondary"
                  onClick={() => toggleParagraphExpansion(paragraphIndex)}
                >
                  Alle {item.sources.length} bronnen
                </Button>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      ref={markdownRef}
      className="markdown-content prose prose-neutral max-w-none"
    >
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

// Add this throttle function at the end of the file or in a utils file
function throttle(func: Function, delay: number) {
  let lastCall = 0;
  return function (...args: any[]) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return func(...args);
    }
  };
}
