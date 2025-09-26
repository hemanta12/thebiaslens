import html2canvas from 'html2canvas';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { AnalyzeResult } from '../types/api';
import { ShareCard } from '../components/analyze/ShareCard';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '../theme';

export const downloadShareCard = async (result: AnalyzeResult): Promise<void> => {
  try {
    // Create a temporary container
    const container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.left = '-9999px';
    container.style.top = '0';
    container.style.width = '1200px';
    container.style.height = '630px';
    document.body.appendChild(container);

    // Create React root and render ShareCard
    const root = ReactDOM.createRoot(container);

    // Render the ShareCard wrapped in ThemeProvider
    await new Promise<void>((resolve) => {
      root.render(
        React.createElement(
          ThemeProvider,
          { theme },
          React.createElement(ShareCard, { data: result }),
        ),
      );

      // Wait for render to complete
      setTimeout(resolve, 100);
    });

    // Capture with html2canvas
    const canvas = await html2canvas(container, {
      width: 1200,
      height: 630,
      backgroundColor: '#ffffff',
      scale: 1,
      useCORS: true,
      allowTaint: true,
    });

    // Clean up the temporary container
    root.unmount();
    document.body.removeChild(container);

    // Download the image
    canvas.toBlob((blob) => {
      if (!blob) {
        throw new Error('Failed to create blob from canvas');
      }

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = `bias-analysis-${result.id}.png`;
      link.href = url;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(url);
    }, 'image/png');
  } catch (error) {
    console.error('Failed to generate share image:', error);
    throw error;
  }
};
