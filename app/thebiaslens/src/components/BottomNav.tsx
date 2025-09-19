import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { BottomNavigation, BottomNavigationAction, Paper } from "@mui/material";
import { Search, Analytics, History, Settings } from "@mui/icons-material";

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  const getNavigationValue = (pathname: string) => {
    switch (pathname) {
      case "/":
        return 0;
      case "/analyze":
        return 1;
      case "/recents":
        return 2;
      case "/settings":
        return 3;
      default:
        return 0;
    }
  };

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    switch (newValue) {
      case 0:
        navigate("/");
        break;
      case 1:
        navigate("/analyze");
        break;
      case 2:
        navigate("/recents");
        break;
      case 3:
        navigate("/settings");
        break;
    }
  };

  return (
    <Paper
      sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}
      elevation={3}
    >
      <BottomNavigation
        value={getNavigationValue(location.pathname)}
        onChange={handleChange}
        showLabels
      >
        <BottomNavigationAction label="Search" icon={<Search />} />
        <BottomNavigationAction label="Analyze" icon={<Analytics />} />
        <BottomNavigationAction label="Recents" icon={<History />} />
        <BottomNavigationAction label="Settings" icon={<Settings />} />
      </BottomNavigation>
    </Paper>
  );
}
