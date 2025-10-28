export interface Message {
  role: "user" | "assistant";
  content: TextParagraph[] | string;
}

export enum SourceType {
  LAW = "law",
  CASE_LAW = "case_law",
  TAXONOMY = "taxonomy",
  WERKINSTRUCTIE = "werkinstructie",
  SELECTIELIJST = "selectielijst",
}

export enum SourceTypeLabel {
  LAW = "Wet",
  CASE_LAW = "Jurisprudentie",
  TAXONOMY = "Definitie",
  WERKINSTRUCTIE = "Werkinstructie",
  SELECTIELIJST = "Selectielijst",
}

interface BaseSource {
  id?: string;
  type: SourceType;
}

interface ISelectielijstRow {
  selectielijsten: string;
  functie: string;
  categorie: string;
  onderwerp: string;
  omschrijving: string;
  waardering: string;
  voorbeeldstukken: string;
  isSource: boolean;
}

interface ISelectielijst {
  name: string;
  rows: ISelectielijstRow[];
}

interface IWerkinstructie {
  title: string;
  url: string;
  isSource: boolean;
  chunks: string[];
}

interface ILaw {
  document?: string;
  title: string;
  law: string;
  url?: string;
  isSource: boolean;
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  lido?: {};
}

interface ICaseLaw {
  document?: string;
  title: string;
  url: string;
  isSource: boolean;
  inhoudsindicatie?: string;
  date_uitspraak?: string;
}

interface ITaxonomy {
  label: string;
  context: Array<{
    id: string;
    isSource: boolean;
    source: string;
    definition: string;
    naderToegelicht: string[];
    wetcontext: {
      url: string;
    };
  }>;
}

// Specifieke source types
export interface LawSource extends BaseSource {
  type: SourceType.LAW;
  value: ILaw;
}

export interface WerkinstructieSource extends BaseSource {
  type: SourceType.WERKINSTRUCTIE;
  value: IWerkinstructie;
}

export interface CaseLawSource extends BaseSource {
  type: SourceType.CASE_LAW;
  value: ICaseLaw;
}

export interface TaxonomySource extends BaseSource {
  type: SourceType.TAXONOMY;
  value: ITaxonomy;
}

export interface SelectielijstSource extends BaseSource {
  id: string;
  type: SourceType.SELECTIELIJST;
  value: ISelectielijst;
}

// Union type voor alle sources (use type instead of interface)
export type Source =
  | LawSource
  | CaseLawSource
  | TaxonomySource
  | SelectielijstSource
  | WerkinstructieSource;

// Text paragraph interface
export interface TextParagraph {
  paragraph: string;
  sources: string[];
}

// Answer interface
export interface Answer {
  text: TextParagraph[];
  sources: Source[];
}

// Root data interface
export interface LegalData {
  answer: Answer;
  sources: Source[];
}

// Filter type
export type TFilter = SourceType | "answer" | "all";
