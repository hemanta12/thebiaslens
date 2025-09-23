import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import { ExtractResult } from '../types/api';

export function useExtract(url: string) {
  return useQuery({
    queryKey: ['extract', url],
    queryFn: () => get<ExtractResult>('/extract', { url }),
    enabled: url.trim().length >= 8,
  });
}
