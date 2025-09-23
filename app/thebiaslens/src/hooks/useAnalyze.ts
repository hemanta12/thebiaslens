import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import { AnalyzeResult } from '../types/api';

export const useAnalyze = (url: string) => {
  return useQuery({
    queryKey: ['analyze', url],
    queryFn: () => get<AnalyzeResult>('/analyze/url', { url }),
    enabled: url.trim().length >= 8, // Match useExtract pattern
  });
};
