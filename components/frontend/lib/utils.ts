import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { SourceType } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function capitalize(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export async function sleep(ms: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export const getTailwindClasses = (sourceType: SourceType) => {
  switch (sourceType) {
    case SourceType.TAXONOMY:
      return "bg-[#FFB611] border-[#FFB611] text-black";
    case SourceType.CASE_LAW:
      return "bg-[#027BC7] border-[#027BC7] text-white";
    case SourceType.SELECTIELIJST:
      return "bg-[#810088] border-[#810088] text-white";
    case SourceType.LAW:
      return "bg-[#77D2B7] border-[#77D2B7] text-black";
    case SourceType.WERKINSTRUCTIE:
      return "bg-[#008000] border-[#008000] text-white";
    default:
      return "";
  }
};
