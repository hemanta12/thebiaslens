export async function get<T>(
  path: string,
  params?: Record<string, string>
): Promise<T> {
  const baseUrl = process.env.REACT_APP_API_BASE_URL;

  if (!baseUrl) {
    throw new Error("REACT_APP_API_BASE_URL environment variable is not set");
  }

  let url = `${baseUrl}${path}`;

  // Build query string if params are provided
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
