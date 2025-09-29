import { useQuery } from '@tanstack/react-query';
import { getFactCheck } from '../api/client';
import type { FactCheckResult } from '../types/api';

export function useFactCheck(args: { headline: string; sourceDomain?: string; summary?: string }) {
  const enabled = Boolean(args?.headline);
  return useQuery<FactCheckResult>({
    queryKey: ['factcheck', args],
    queryFn: async () => {
      return await getFactCheck({
        headline: args.headline,
        sourceDomain: args.sourceDomain,
        summary: args.summary,
      });
    },
    enabled,
    staleTime: 5 * 60 * 1000,
  });
}
