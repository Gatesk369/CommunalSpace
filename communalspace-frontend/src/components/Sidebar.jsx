import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Home,
  Store,
  Megaphone,
  Bell,
  Settings,
  User,
  ArrowLeftToLine,
} from "lucide-react";

const mainLinks = [
  { label: "Home", icon: Home },
  { label: "Businesses", icon: Store },
  { label: "Announcements", icon: Megaphone },
  { label: "Notifications", icon: Bell },
];

const bottomLinks = [
  { label: "Settings", icon: Settings },
  { label: "Profile", icon: User },
];

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const sidebarRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event) {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  return (
    <motion.div
      ref={sidebarRef}
      onClick={() => setIsOpen((prev) => !prev)}
      initial={false}
      animate={{
        width: isOpen ? 316 : 208,
        height: isOpen ? "100vh" : 80,
      }}
      transition={{ type: "tween", duration: 0.4, ease: [0, 0.4, 0.15, 1] }}
      className="fixed top-0 left-0 z-[60] flex flex-col bg-[linear-gradient(theme(colors.cs-coral)_0%,theme(colors.cs-orange)_30%)] rounded-r-[45px] overflow-visible cursor-pointer"
    >
      <div className="h-20 flex items-center justify-between flex-shrink-0">
        <motion.p
          animate={{ paddingLeft: isOpen ? 24 : 48 }}
          transition={{ type: "tween", duration: 0.6, ease: [0, 0.4, 0.1, 1] }}
          className="text-[30px] font-bold whitespace-nowrap"
        >
          <span className="text-white">Communal</span>{" "}
          <motion.span
            animate={{ color: isOpen ? "#ffffff" : "#F97316" }}
            transition={{ duration: 0.25 }}
          >
            Space
          </motion.span>
        </motion.p>

        {isOpen && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsOpen(false);
            }}
            className="mt-2 mr-3 text-white/80 hover:text-white transition-colors"
          >
            <ArrowLeftToLine size={24} />
          </button>
        )}
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="flex-1 flex flex-col justify-between px-6 pb-6 cursor-default"
          >
            <nav className="flex flex-col gap-3 mt-12">
              {mainLinks.map(({ label, icon: Icon }) => (
                <div
                  key={label}
                  className="flex items-center gap-3 px-5 py-3 rounded-full font-semibold bg-white/20 text-white"
                >
                  <Icon size={20} />
                  {label}
                </div>
              ))}
            </nav>

            <nav className="flex flex-col gap-2">
              {bottomLinks.map(({ label, icon: Icon }) => (
                <div
                  key={label}
                  className="flex items-center gap-3 px-3 py-2 rounded-full font-medium text-white/80"
                >
                  <Icon size={18} />
                  {label}
                </div>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
