import React from 'react'
import { cn } from '@/lib/utils'  // adjust the import path if needed

interface ValidationTextProps {
  text: string;
  mood: "error" | "success" | "warning";
  size: "small" | "medium" | "large";
  className?: string;
}

const moodClasses = {
  error: "text-robijnrood",  // uses --color-robijnrood from globals.css
  success: "text-groen",     // uses --color-groen from globals.css
  warning: "text-oranje",    // uses --color-oranje from globals.css
}

const sizeClasses = {
  small: "text-sm",
  medium: "text-base",
  large: "text-lg",
}

const ValidationText = ({ text, mood, size, className }: ValidationTextProps) => {
  return (
    <div className={cn(className, sizeClasses[size], moodClasses[mood])}>
      {text}
    </div>
  )
}

export default ValidationText
