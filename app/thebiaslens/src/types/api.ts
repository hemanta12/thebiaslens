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
  confidence: number;
  score: number;
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

export type FactCheckRequest = {
  headline: string;
  sourceDomain?: string;
  summary?: string;
  maxAgeMonths?: number;
};

export type FactCheckItem = {
  claim: string;
  verdict?: string | null;
  snippet?: string | null;
  source?: string | null;
  url?: string | null;
  matchReason?: string;
  publishedAt?: string | null;
  similarity?: number | null;
};

export type FactCheckResult = {
  status: 'found' | 'none';
  items: FactCheckItem[];
};

export type Paged<T> = {
  items: T[];
  nextCursor?: string | null;
};
