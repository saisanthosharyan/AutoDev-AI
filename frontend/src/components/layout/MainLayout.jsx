import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function MainLayout({ children }) {
  return (
    <div className="h-screen w-screen flex bg-slate-950 text-white overflow-hidden">

      {/* Sidebar */}
      <Sidebar />

      {/* Right Side */}
      <div className="flex flex-col flex-1">

        {/* Navbar */}
        <Navbar />

        {/* Page */}
        <main className="flex-1 overflow-y-auto bg-slate-900">
          {children}
        </main>

      </div>

    </div>
  );
}