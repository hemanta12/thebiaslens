import React from "react";
import { Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import Header from "./Header";
import BottomNav from "./BottomNav";

export default function Layout() {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1, pb: 7 }}>
        <Outlet />
      </Box>
      <BottomNav />
    </Box>
  );
}
