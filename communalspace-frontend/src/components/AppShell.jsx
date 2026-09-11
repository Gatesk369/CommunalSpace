import { Outlet } from "react-router-dom";
import Navbar1 from "./Navbar1";
import Sidebar from "./Sidebar";

export default function AppShell() {
  return (
    <div className="bg-cs-bg min-h-screen">
      <Sidebar />
      <Navbar1 />
      <main className="pt-20 pl-118">
        <Outlet />
      </main>
    </div>
  );
}
