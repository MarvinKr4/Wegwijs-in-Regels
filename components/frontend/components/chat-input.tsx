import React, { useEffect, KeyboardEvent } from "react";
import { cn } from "@/lib/utils";
import { WandSparkles } from "lucide-react";
import { Textarea } from "./ui/textarea";
import ValidationText from "./validation-text";

interface ChatInputProps {
  text: string;
  setText: (text: string) => void;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  isOpen: boolean;
  validationText: string;
}

const chatSuggestions = [
  "Welke persoonsgegevens mag ik inzien?",
  "Wat valt er onder het Woo-verzoek wat ik heb gekregen?",
  "Hoe lang moet ik deze data bewaren?",
];

export const ChatInput = ({
  text,
  setText,
  handleKeyDown,
  isOpen,
  validationText,
}: ChatInputProps) => {
  const [pendingSubmission, setPendingSubmission] = React.useState<
    string | null
  >(null);

  useEffect(() => {
    if (pendingSubmission && text === pendingSubmission) {
      handleKeyDown({
        key: "Enter",
        shiftKey: false,
        preventDefault: () => {},
      } as KeyboardEvent<HTMLTextAreaElement>);
      setPendingSubmission(null);
    }
  }, [text, pendingSubmission, handleKeyDown]);

  if (isOpen) return null;
  return (
    <div className="relative w-full flex items-center justify-center flex-col">
      <div className={cn("w-full relative h-fit", { "max-w-3xl": !isOpen })}>
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Stel een vraag over de AVG, Woo of archiefwet"
          className={cn(
            "transition-all rounded-2xl duration-300 relative pr-16",
            isOpen ? "w-full" : "max-w-3xl"
          )}
        />
        <WandSparkles className="ml-4 absolute top-1/2 right-12 -translate-y-1/2 text-lintblauw" />
      </div>
      {validationText && (
        <ValidationText
          className="text-center pt-2 pb-3"
          text={validationText}
          mood="error"
          size="small"
        />
      )}
      <div className="w-full max-w-[800px] pt-4 h-fit overflow-hidden flex-wrap flex gap-4 text-center items-center justify-center">
        {chatSuggestions.map((suggestion) => (
          <div
            key={suggestion}
            onClick={() => {
              setText(suggestion);
              setPendingSubmission(suggestion);
            }}
            className="text-center text-sm p-2 bg-grijs-1 rounded-2xl text-black whitespace-nowrap cursor-pointer"
          >
            {suggestion}
          </div>
        ))}
      </div>
    </div>
  );
};
