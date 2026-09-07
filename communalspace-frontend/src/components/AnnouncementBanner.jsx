import { X } from "lucide-react";
import { motion } from "motion/react";

export default function AnnouncementBanner({
  urgency = "CRITICAL",
  message,
  onDismiss,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-[804px] drop-shadow-lg flex items-center gap-4 bg-[linear-gradient(90deg,theme(colors.cs-orange)_0%,theme(colors.cs-magenta)_60%,theme(colors.cs-purple)_100%)] rounded-full px-4 py-3 mb-6"
    >
      <span className="bg-white/25 text-white text-xs font-extrabold tracking-wide uppercase px-3 py-1 rounded-full flex-shrink-0">
        {urgency}
      </span>
      <p className="text-white text-sm font-semibold flex-1">{message}</p>
      <button
        onClick={onDismiss}
        className="text-white/90 hover:text-white flex-shrink-0"
      >
        <X size={18} />
      </button>
    </motion.div>
  );
}
