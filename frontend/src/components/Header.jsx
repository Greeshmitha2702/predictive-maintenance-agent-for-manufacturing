import { NavLink } from "react-router-dom";

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div>
          <h1>Predictive Maintenance</h1>
          <p>Manufacturing Machine Health Dashboard</p>
        </div>

        <nav className="navigation">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Home
          </NavLink>

          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/analysis"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Analysis
          </NavLink>

          <NavLink
          to="/history"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
           }
          >
            History
          </NavLink>

          <NavLink
            to="/about"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            System Overview
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;