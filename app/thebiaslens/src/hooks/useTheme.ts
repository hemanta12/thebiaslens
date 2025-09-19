import { useTheme } from "@mui/material/styles";

// Custom hook to access the theme
export const useAppTheme = () => {
  const theme = useTheme();
  return theme;
};

// Hook to get common theme values
export const useThemeColors = () => {
  const theme = useTheme();
  return {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    background: theme.palette.background.default,
    paper: theme.palette.background.paper,
    text: theme.palette.text.primary,
  };
};
