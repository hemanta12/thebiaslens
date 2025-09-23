import { useQuery } from '@tanstack/react-query';
import { useState, useEffect, useMemo } from 'react';
import { get } from '../api/client';
import { ArticleStub, Paged } from '../types/api';

export function useSearchPaged(query: string) {
  const [cursor, setCursor] = useState(1);
  const [allPages, setAllPages] = useState<Paged<ArticleStub>[]>([]);

  // Reset cursor and pages when query changes
  useEffect(() => {
    setCursor(1);
    setAllPages([]);
  }, [query]);

  const { data, isLoading, error, isError } = useQuery({
    queryKey: ['search', query, cursor],
    queryFn: () =>
      get<Paged<ArticleStub>>('/search', {
        q: query,
        cursor: cursor.toString(),
      }),
    enabled: query.trim().length >= 2,
  });

  // Update allPages when new data arrives
  useEffect(() => {
    if (data) {
      setAllPages((prev) => {
        if (cursor === 1) {
          return [data];
        }
        return [...prev, data];
      });
    }
  }, [data, cursor]);

  // Concatenate all items from all pages
  const items = useMemo(() => {
    return allPages.flatMap((page) => page.items);
  }, [allPages]);

  // Check if there's a next page based on the last response
  const hasNext = useMemo(() => {
    const lastPage = allPages[allPages.length - 1];
    return Boolean(lastPage?.nextCursor);
  }, [allPages]);

  // Function to load more results
  const loadMore = () => {
    const lastPage = allPages[allPages.length - 1];
    if (lastPage?.nextCursor) {
      setCursor(Number(lastPage.nextCursor));
    }
  };

  // Check if we're loading more (not the initial load)
  const isLoadingMore = isLoading && cursor > 1;

  return {
    items,
    hasNext,
    loadMore,
    isLoading,
    isLoadingMore,
    error,
    isError,
  };
}
