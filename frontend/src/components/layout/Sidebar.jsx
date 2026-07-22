import { NavLink } from "react-router-dom";
import {
  Home,
  FolderGit2,
  Settings,
  History,
} from "lucide-react";

export default function Sidebar() {
  const menu = [
    {
      name: "Home",
      icon: <Home size={20} />,
      path: "/",
    },
    {
      name: "Projects",
      icon: <FolderGit2 size={20} />,
      path: "/projects",
    },
    {
      name: "History",
      icon: <History size={20} />,
      path: "#",
    },
    {
      name: "Settings",
      icon: <Settings size={20} />,
      path: "#",
    },
  ];

  return (
    <aside className="w-72 bg-black border-r border-gray-800 flex flex-col">
      <div className="text-3xl font-bold p-8">
        🚀 AutoDev AI
      </div>

      <nav className="flex flex-col gap-3 px-4">
        {menu.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg p-4 transition ${
                isActive
                  ? "bg-cyan-600 text-white"
                  : "hover:bg-gray-800 text-gray-300"
              }`
            }
          >
            {item.icon}
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto p-6 text-gray-500 text-sm">
        Version 1.0
      </div>
    </aside>
  );
}