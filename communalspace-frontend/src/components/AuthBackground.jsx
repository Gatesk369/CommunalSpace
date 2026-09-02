// components/AuthBackground.jsx
import { motion } from "motion/react";

export default function AuthBackground({ children }) {
  return (
    <div className="font-google-sans w-screen h-screen relative overflow-hidden flex items-center justify-center bg-[linear-gradient(45deg,theme(colors.cs-orange)_0%,theme(colors.cs-coral)_30%,theme(colors.cs-magenta)_65%,theme(colors.cs-purple)_100%)]">
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 2, ease: [1, 0, 0, 1] }}
        className="absolute drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] w-[1540px] h-[1750px]"
      >
        <motion.div
          animate={{ rotate: [30, 50] }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse",
            ease: [0.65, 0, 0.35, 1],
          }}
          className="w-full h-full rounded-[50%] bg-[linear-gradient(45deg,theme(colors.cs-orange)_0%,theme(colors.cs-coral)_30%,theme(colors.cs-magenta)_65%,theme(colors.cs-purple)_100%)]"
        />
      </motion.div>
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 2, ease: [1, 0, 0, 1] }}
        className="absolute drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] w-[1040px] h-[1150px]"
      >
        <motion.div
          animate={{ rotate: [-50, -30] }}
          transition={{
            duration: 10,
            repeat: Infinity,
            repeatType: "reverse",
            ease: [0.65, 0, 0.35, 1],
          }}
          className="w-full h-full rounded-[50%] bg-[linear-gradient(45deg,theme(colors.cs-orange)_0%,theme(colors.cs-coral)_30%,theme(colors.cs-magenta)_65%,theme(colors.cs-purple)_100%)]"
        />
      </motion.div>
      {children}
    </div>
  );
}
