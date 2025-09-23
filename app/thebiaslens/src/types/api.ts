export type ArticleStub = {
  url: string;
  source: string;
  publishedAt: string;
  title: string;
  extractStatus?: 'api' | 'extracted' | 'missing';
};

export type ExtractResult = {
  url: string;
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
  extract: ExtractResult;
  summary?: SummaryResult | null;
};

export type Paged<T> = {
  items: T[];
  nextCursor?: string | null;
};
