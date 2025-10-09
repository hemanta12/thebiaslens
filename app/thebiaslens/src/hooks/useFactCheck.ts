import { useQuery } from '@tanstack/react-query';
import { getFactCheck } from '../api/client';
import type { FactCheckResult } from '../types/api';

export function useFactCheck(args: {
  headline: string;
  sourceDomain?: string;
  summary?: string;
  maxAgeMonths?: number;
}) {
  const enabled = Boolean(args?.headline);
  return useQuery<FactCheckResult>({
    queryKey: [
      'factcheck',
      {
        headline: args.headline,
        sourceDomain: args.sourceDomain,
        summary: args.summary,
        maxAgeMonths: args.maxAgeMonths || 18,
      },
    ],
    queryFn: async () => {
      return await getFactCheck({
        headline: args.headline,
        sourceDomain: args.sourceDomain,
        summary: args.summary,
        maxAgeMonths: args.maxAgeMonths || 18,
      });
    },
    enabled,
    staleTime: 5 * 60 * 1000,
  });
}
