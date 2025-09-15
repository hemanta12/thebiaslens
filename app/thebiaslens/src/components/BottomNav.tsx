import React from "react";
import { NavLink } from "react-router-dom";

export default function BottomNav() {
  return (
    <nav role="navigation" aria-label="Primary">
      <div>
        <NavLink
          to="/"
          end
          className={({ isActive }: { isActive: boolean }) =>
            isActive ? "active" : undefined
          }
        >
          Search
        </NavLink>
      </div>
      <div>
        <NavLink
          to="/analyze"
          className={({ isActive }: { isActive: boolean }) =>
            isActive ? "active" : undefined
          }
        >
          Analyze
        </NavLink>
      </div>
      <div>
        <NavLink
          to="/recents"
          className={({ isActive }: { isActive: boolean }) =>
            isActive ? "active" : undefined
          }
        >
          Recents
        </NavLink>
      </div>
      <div>
        <NavLink
          to="/settings"
          className={({ isActive }: { isActive: boolean }) =>
            isActive ? "active" : undefined
          }
        >
          Settings
        </NavLink>
      </div>
    </nav>
  );
}
