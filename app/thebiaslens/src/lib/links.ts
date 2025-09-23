export const buildAnalyzeLink = (id: string, url: string) =>
  `/analyze/${encodeURIComponent(id)}?url=${encodeURIComponent(url)}`;
