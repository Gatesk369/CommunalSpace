import { X } from "lucide-react";
import { motion } from "motion/react";

const URGENCY_STYLES = {
  info: "bg-[linear-gradient(90deg,theme(colors.cs-orange)_0%,theme(colors.cs-red)_100%)]",
  warning:
    "bg-[linear-gradient(90deg,theme(colors.cs-orange)_0%,theme(colors.cs-magenta)_100%)]",
  critical:
    "bg-[linear-gradient(90deg,theme(colors.cs-orange)_0%,theme(colors.cs-magenta)_60%,theme(colors.cs-purple)_100%)]",
};

export default function AnnouncementBanner({
  urgency = "info",
  message,
  onDismiss,
}) {
  const gradientClass = URGENCY_STYLES[urgency] || URGENCY_STYLES.info;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`drop-shadow-lg flex items-center gap-4 ${gradientClass} rounded-full px-4 py-3 mb-6`}
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
