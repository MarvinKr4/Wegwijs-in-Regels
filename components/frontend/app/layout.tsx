import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

if (process.env.NEXT_API_MOCKING_ENABLED) {
  require("../mocks");
}

const rijksOverheidFont = localFont({
  src: [
    {
      path: "../fonts/rijksoverheidsansheading-bold.ttf",
      weight: "400",
      style: "bold",
    },
    {
      path: "../fonts/rijksoverheidsanstext-regular.ttf",
      weight: "400",
      style: "normal",
    },
    // {
    //   path: '../fonts/rijksoverheidserif-italic.ttf',
    //   weight: '400',
    //   style: 'italic',
    // },
    // {
    //   path: '../fonts/rijksoverheidserif-regular.ttf',
    //   weight: '400',
    //   style: 'normal',
    // },
  ],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Wegwijs in Regels",
  description: "Wegwijs in Regels",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${rijksOverheidFont.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
