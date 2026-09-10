import { useState } from "react";
import { motion } from "motion/react";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <motion.button
        onClick={() => setIsOpen((prev) => !prev)}
        className="fixed top-0 left-0 h-20 w-51 z-60 flex items-center bg-[linear-gradient(theme(colors.cs-coral)_0%,theme(colors.cs-orange)_30%)] rounded-r-[70px] whitespace-nowrap"
      >
        <p className="pl-12 text-[30px] font-semibold">
          <span className="text-white">Communal</span> Space
        </p>
      </motion.button>

      {isOpen && (
        <div className="fixed top-0 left-0 h-screen w-75 bg-white border-r-2 border-cs-line z-55 pt-20">
          {/* nav links, settings, profile go here next */}
        </div>
      )}
    </>
  );
}
