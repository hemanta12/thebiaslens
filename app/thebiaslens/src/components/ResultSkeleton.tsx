import React from 'react';
import { Box, Skeleton, Stack } from '@mui/material';

const ResultSkeleton = () => {
  return (
    <Stack spacing={2}>
      {[...Array(3)].map((_, index) => (
        <Box
          key={index}
          sx={{
            p: 2,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}
        >
          <Skeleton variant="text" width="60%" height={24} />
          <Skeleton variant="text" width="40%" height={20} sx={{ mt: 1 }} />
          <Skeleton variant="rectangular" width="100%" height={60} sx={{ mt: 2 }} />
        </Box>
      ))}
    </Stack>
  );
};

export default ResultSkeleton;
