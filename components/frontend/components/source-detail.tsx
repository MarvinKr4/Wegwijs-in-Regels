"use client";

import React from "react";
import { Source, SourceType } from "@/lib/types";
import { ArrowLeft } from "lucide-react";
import { Button } from "./ui/button";
import { SourceBadgeText } from "./source-badge-text";
import { cn, getTailwindClasses } from "@/lib/utils";
import { MarkdownRenderer } from "./markdown-renderer";

interface SourceDetailProps {
  source: Source;
  onBack: () => void;
}

export const SourceDetail = ({ source, onBack }: SourceDetailProps) => {
  const renderSourceContent = () => {
    switch (source.type) {
      case SourceType.LAW:
        return (
          <div className="space-y-4">
            {source.value.url && (
              <a
                href={source.value.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline pb-4 block"
              >
                Bekijk op overheid.nl
              </a>
            )}
            <h2 className="text-xl font-semibold">{source.value.law}</h2>
            {source.value.document && (
              <div className="">
                <MarkdownRenderer content={source.value.document} />
              </div>
            )}
          </div>
        );

      case SourceType.CASE_LAW:
        return (
          <div className="space-y-4">
            {source.value.url && (
              <a
                href={source.value.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline pb-4 block"
              >
                Bekijk op rechtspraak.nl
              </a>
            )}
            <h2 className="text-xl font-semibold">{source.value.title}</h2>
            <div className="space-y-2">
              {source.value.inhoudsindicatie && (
                <div className="text-sm">
                  <span className="text-slate-400">Inhoudsindicatie: </span>
                  {source.value.inhoudsindicatie}
                </div>
              )}
              {source.value.date_uitspraak && (
                <div className="text-sm">
                  <span className="text-slate-400">Datum uitspraak: </span>
                  {source.value.date_uitspraak}
                </div>
              )}
            </div>
            {source.value.document && (
              <div className="pt-4">
                <MarkdownRenderer content={source.value.document} />
              </div>
            )}
          </div>
        );

      case SourceType.TAXONOMY:
        return (
          <div className="space-y-6">
            <div className="space-y-1">
              <div className="text-sm text-slate-400">Definitie</div>
              <div className="font-medium text-lg">{source.value.label}</div>
            </div>

            {source.value.context.map((ctx, index) => (
              <div key={index} className="space-y-4">
                <div className="relative pl-6">
                  <div className="font-medium">{ctx.definition}</div>
                  {/* L-shaped connector */}
                  <div className="absolute left-[7px] top-[12px] h-[1px] w-3 border-t border-dashed border-slate-400" />
                  <div className="absolute left-[7px] top-0 h-[12px] border-l border-dashed border-slate-400" />
                </div>

                {ctx.source && (
                  <a
                    href={ctx.source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline block"
                  >
                    Bekijk de bron
                  </a>
                )}

                {ctx.wetcontext?.url && (
                  <a
                    href={ctx.wetcontext.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline block"
                  >
                    Bekijk wetcontext
                  </a>
                )}

                {ctx.naderToegelicht && ctx.naderToegelicht.length > 0 && (
                  <div className="relative pl-6">
                    <div className=" text-slate-400">
                      Richtlijn gegevensbescherming bij rechtshandhaving
                    </div>
                    <div>
                      {ctx.naderToegelicht.map((item, i) => (
                        <a
                          key={i}
                          href={item}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline block"
                        >
                          {item}
                        </a>
                      ))}
                    </div>
                    {/* L-shaped connector */}
                    <div className="absolute left-[13px] top-[12px] h-[1px] w-3 border-t border-dashed border-slate-400" />
                    <div className="absolute left-[13px] top-0 h-[12px] border-l border-dashed border-slate-400" />
                  </div>
                )}

                {index < source.value.context.length - 1 && (
                  <div className="pt-4" />
                )}
              </div>
            ))}
          </div>
        );

      case SourceType.SELECTIELIJST:
        return (
          <div className="space-y-6">
            {source.value.rows.map((row, index) => (
              <div key={index} className="space-y-4">
                <div className="space-y-1">
                  <div className="text-sm text-slate-400">Proces</div>
                  <div className="font-medium text-lg">{row.categorie}</div>
                </div>

                <div className="relative pl-6">
                  <div className="text-sm text-slate-400">Onderwerp</div>
                  <div className="font-medium">{row.onderwerp}</div>
                  {/* L-shaped connector */}
                  <div className="absolute left-[7px] top-[12px] h-[1px] w-3 border-t border-dashed border-slate-400" />
                  <div className="absolute left-[7px] top-0 h-[12px] border-l border-dashed border-slate-400" />
                </div>

                <div className="relative pl-12">
                  <div className="text-sm text-slate-400">Bewaartermijn</div>
                  <div>{row.waardering}</div>
                  {/* L-shaped connector */}
                  <div className="absolute left-[13px] top-[12px] h-[1px] w-3 border-t border-dashed border-slate-400" />
                  <div className="absolute left-[13px] top-0 h-[12px] border-l border-dashed border-slate-400" />
                </div>

                <div className="relative pl-12">
                  <div className="text-sm text-slate-400">Voorbeeldstukken</div>
                  <div>{row.voorbeeldstukken}</div>
                  {/* L-shaped connector */}
                  <div className="absolute left-[13px] top-[12px] h-[1px] w-3 border-t border-dashed border-slate-400" />
                  <div className="absolute left-[13px] top-0 h-[12px] border-l border-dashed border-slate-400" />
                </div>

                {index < source.value.rows.length - 1 && (
                  <div className="pt-4 border-b" />
                )}
              </div>
            ))}
          </div>
        );

      case SourceType.WERKINSTRUCTIE:
        return (
          <div className="space-y-4">
            {source.value.url && (
              <a
                href={source.value.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline pb-4 block"
              >
                Bekijk werkinstructie
              </a>
            )}
            <h2 className="text-xl font-semibold">{source.value.title}</h2>
            {source.value.chunks.map((chunk, index) => (
              <div key={index} className="space-y-2">
                <MarkdownRenderer content={chunk} />
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="h-full flex flex-col pl-8 source-detail-container">
      <div className="flex items-center gap-2 pt-4 border-b">
        <Button
          variant="ghost"
          size="icon"
          onClick={onBack}
          className="shrink-0"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <SourceBadgeText sourceType={source.type} />
      </div>
      <div className="flex-1 overflow-auto pb-12">
        <div className="relative  px-4 pt-6">
          <div
            className={cn(
              "absolute w-1 left-0 top-0 h-full",
              getTailwindClasses(source.type)
            )}
          />
          {renderSourceContent()}
        </div>
      </div>
    </div>
  );
};
