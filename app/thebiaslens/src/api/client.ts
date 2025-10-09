import type { FactCheckResult, FactCheckRequest } from '../types/api';

export async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

  if (!baseUrl) {
    throw new Error('REACT_APP_API_BASE_URL environment variable is not set');
  }

  let url = `${baseUrl}${path}`;

  if (params && Object.keys(params).length > 0) {
    const queryString = new URLSearchParams(params).toString();
    url += `?${queryString}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getFactCheck(req: FactCheckRequest): Promise<FactCheckResult> {
  const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

  if (!baseUrl) {
    throw new Error('REACT_APP_API_BASE_URL environment variable is not set');
  }

  const response = await fetch(`${baseUrl}/factcheck`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      headline: req.headline,
      sourceDomain: req.sourceDomain,
      summary: req.summary,
      maxAgeMonths: req.maxAgeMonths || 18,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch fact checks');
  }

  return response.json() as Promise<FactCheckResult>;
}
