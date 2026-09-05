import { motion } from "motion/react";

export default function LoadingButton({
  isLoading,
  loadingText = "Loading...",
  children,
  ...props
}) {
  return (
    <motion.button
      {...props}
      disabled={isLoading}
      whileHover={!isLoading ? { scale: 1.03 } : {}}
      whileTap={!isLoading ? { scale: 0.96 } : {}}
      animate={{
        backgroundColor: isLoading ? "#c937c7" : "#F97316",
      }}
      transition={{
        backgroundColor: isLoading
          ? {
              duration: 0.9,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
            }
          : { duration: 0.3, ease: "easeOut" },
      }}
      className="w-[80%] text-white text-xl font-bold rounded-full py-3.5 mt-2"
    >
      {isLoading ? loadingText : children}
    </motion.button>
  );
}
