import { motion } from "motion/react";

export default function Navbar1() {
  return (
    <nav className="font-google-sans bg-white border-b-2 border-cs-line w-full z-50 top-0 h-20 fixed">
      <div className="flex items-center justify-between w-full h-full">
        <motion.div className="flex items-center h-full bg-[linear-gradient(theme(colors.cs-coral)_0%,theme(colors.cs-orange)_30%)] w-52 rounded-r-[70px] whitespace-nowrap">
          <p className="pl-12 text-[30px] font-semibold">
            <span className="text-white">Communal</span> Space
          </p>
        </motion.div>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="absolute -top-15 left-1/2 -translate-x-1/2 h-40 w-50 bg-[linear-gradient(theme(colors.cs-coral)_0%,theme(colors.cs-orange)_60%)] rounded-[50%] flex items-center justify-center z-50"
        >
          <span className="pt-10 text-white text-[28px] font-semibold">
            Kisaasi
          </span>
        </motion.button>
        <div className="absolute top-1/2 right-8 -translate-y-1/2 z-50">
          <div className="w-14 h-14 rounded-full bg-[radial-gradient(circle_at_35%_35%,theme(colors.cs-orange)_0%,theme(colors.cs-magenta)_60%,theme(colors.cs-purple)_100%)]" />
        </div>
      </div>
    </nav>
  );
}
