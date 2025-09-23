import { useQuery } from '@tanstack/react-query';
import { SummaryResult } from '../types/api';

export function useSummarize(text: string, enabled: boolean) {
  return useQuery({
    queryKey: ['summarize', text],
    queryFn: async () => {
      const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${baseUrl}/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json() as Promise<SummaryResult>;
    },
    enabled: enabled && text.length >= 200,
  });
}
