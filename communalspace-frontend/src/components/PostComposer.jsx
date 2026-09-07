import { motion } from "motion/react";
import { Image as ImageIcon } from "lucide-react";

export default function PostComposer() {
  return (
    <div className="bg-white border-2 border-cs-line rounded-3xl p-5 mb-6">
      <div className="flex items-center gap-3 border-2 border-cs-line rounded-2xl px-4 py-3">
        <div className="w-10 h-10 rounded-full bg-cs-magenta flex-shrink-0" />
        <input
          type="text"
          placeholder="Share something with your community..."
          className="flex-1 outline-none text-sm text-cs-ink placeholder:text-cs-muted"
        />
      </div>
      <div className="flex items-center justify-between mt-4">
        <button className="w-10 h-10 rounded-full border-2 border-cs-line flex items-center justify-center text-cs-muted hover:text-cs-orange hover:border-cs-orange transition-colors">
          <ImageIcon size={18} />
        </button>
        <motion.button
          whileTap={{ scale: 0.96 }}
          className="bg-cs-orange text-white font-bold text-sm px-6 py-2 rounded-full"
        >
          Post
        </motion.button>
      </div>
    </div>
  );
}
