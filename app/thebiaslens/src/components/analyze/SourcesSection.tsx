import React, { useMemo } from 'react';
import { Box, Typography, Link as MuiLink } from '@mui/material';

type Props = {
  sourceDomain: string;
  canonicalUrl: string;
  bodyText?: string;
};

const urlRegex = /https?:\/\/[\w.-]+(?:\/[\w\-._~:/?#[\]@!$&'()*+,;=%]*)?/gi;

const getHost = (u: string) => {
  try {
    return new URL(u).host.toLowerCase();
  } catch {
    return '';
  }
};

const SourcesSection: React.FC<Props> = ({ sourceDomain, canonicalUrl, bodyText }) => {
  const refs = useMemo(() => {
    if (!bodyText) return [] as string[];
    const found = (bodyText.match(urlRegex) || []).slice(0, 50); // cap raw finds
    const uniqueByHost = new Map<string, string>();
    for (const u of found) {
      const host = getHost(u);
      if (!host) continue;
      if (!uniqueByHost.has(host) && !canonicalUrl.includes(u)) {
        uniqueByHost.set(host, u);
      }
      if (uniqueByHost.size >= 5) break; // keep up to 5
    }
    return Array.from(uniqueByHost.values());
  }, [bodyText, canonicalUrl]);

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
        Sources & Citations
      </Typography>
      <Box sx={{ fontSize: '14px', color: 'text.secondary' }}>
        <div style={{ marginBottom: 8 }}>
          <span style={{ color: '#666' }}>Primary:</span>{' '}
          <MuiLink href={canonicalUrl} target="_blank" rel="noopener noreferrer" color="primary">
            {sourceDomain}
          </MuiLink>
        </div>
        {refs.length > 0 && (
          <ul style={{ margin: 0, paddingLeft: 18, listStyle: 'disc', color: '#90a4ae' }}>
            {refs.map((u, i) => (
              <li key={i} style={{ marginBottom: 4 }}>
                <MuiLink href={u} target="_blank" rel="noopener noreferrer" color="primary">
                  {getHost(u) || u}
                </MuiLink>
              </li>
            ))}
          </ul>
        )}
      </Box>
    </Box>
  );
};

export default SourcesSection;
