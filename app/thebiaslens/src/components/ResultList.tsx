import React from 'react';
import { List, ListItem, ListItemText, Link, Typography, Button, Box } from '@mui/material';
import { ArticleStub } from '../types/api';

interface ResultListProps {
  items: ArticleStub[];
  onLoadMore?: () => void;
  hasNext?: boolean;
  isLoadingMore?: boolean;
}

const ResultList: React.FC<ResultListProps> = ({
  items,
  onLoadMore,
  hasNext = false,
  isLoadingMore = false,
}) => {
  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <>
      <List className="space-y-2">
        {items.map((item) => (
          <ListItem
            key={item.url}
            component={Link}
            href={item.url}
            target="_blank"
            rel="noopener"
            sx={{
              display: 'block',
              textDecoration: 'none',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              mb: 1,
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <ListItemText
              primary={
                <Typography variant="subtitle1" color="text.primary">
                  {item.title}
                </Typography>
              }
              secondary={
                <Typography variant="body2" color="text.secondary">
                  {item.source} • {formatDate(item.publishedAt)}
                </Typography>
              }
            />
          </ListItem>
        ))}
      </List>

      {/* Load More Button */}
      {hasNext && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button
            variant="outlined"
            onClick={onLoadMore}
            disabled={isLoadingMore}
            sx={{ minWidth: 120 }}
          >
            {isLoadingMore ? 'Loading...' : 'Load more'}
          </Button>
        </Box>
      )}
    </>
  );
};

export default ResultList;
