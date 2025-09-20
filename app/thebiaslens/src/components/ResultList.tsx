import React from 'react';
import { List, ListItem, ListItemText, Link, Typography } from '@mui/material';
import { ArticleStub } from '../types/api';

interface ResultListProps {
  items: ArticleStub[];
}

const ResultList: React.FC<ResultListProps> = ({ items }) => {
  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
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
  );
};

export default ResultList;
