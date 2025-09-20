export type ArticleStub = {
  url: string;
  source: string;
  publishedAt: string;
  title: string;
  extractStatus?: "api" | "extracted" | "missing";
};

export type Paged<T> = {
  items: T[];
  nextCursor?: string | null;
};
