export type ArticleStub = {
  url: string;
  source: string;
  publishedAt: string;
  title: string;
  extractStatus?: 'api' | 'extracted' | 'missing';
};

export type BiasLabel = 'Left' | 'Neutral' | 'Right';

export type BiasResult = {
  label: BiasLabel;
  confidence: number; // [0..1]
  score: number; // [-1..1] where -1 left, 0 neutral, +1 right
  calibrationVersion: string;
};

export type ExtractResult = {
  url: string;
  canonicalUrl?: string;
  headline?: string;
  source: string;
  publishedAt?: string;
  author?: string;
  body?: string;
  wordCount: number;
  extractStatus: 'extracted' | 'missing' | 'error';
  paywalled?: boolean;
};

export type SummaryResult = {
  sentences: string[];
  joined: string;
  charCount: number;
  wordCount: number;
};

export type AnalyzeResult = {
  id: string;
  canonicalUrl: string;
  extract: ExtractResult;
  summary?: SummaryResult | null;
  bias?: BiasResult | null;
};

export type Paged<T> = {
  items: T[];
  nextCursor?: string | null;
};
