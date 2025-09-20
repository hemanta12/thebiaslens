import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import { ArticleStub, Paged } from '../types/api';

export function useSearch(query: string) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => get<Paged<ArticleStub>>('/search', { q: query }),
    enabled: query.trim().length >= 2,
  });
}
