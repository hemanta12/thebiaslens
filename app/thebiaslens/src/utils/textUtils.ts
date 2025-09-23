export const formatDate = (dateString?: string): string | null => {
  if (!dateString) return null;
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return dateString;
  }
};

export const getPreviewText = (text: string, maxLength: number = 600): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};
