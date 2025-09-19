import React from "react";
import { AppBar, Toolbar, Typography, IconButton } from "@mui/material";
import { Share, OpenInNew } from "@mui/icons-material";

interface HeaderProps {
  title?: string;
}

export default function Header({ title = "TheBiasLens" }: HeaderProps) {
  const handleShare = () => {
    // Placeholder for share functionality
    console.log("Share clicked");
  };

  const handleOpenOriginal = () => {
    // Placeholder for open original functionality
    console.log("Open original clicked");
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
        <IconButton
          edge="end"
          color="inherit"
          aria-label="share"
          onClick={handleShare}
        >
          <Share />
        </IconButton>
        <IconButton
          edge="end"
          color="inherit"
          aria-label="open original"
          onClick={handleOpenOriginal}
        >
          <OpenInNew />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}
