import { motion } from "motion/react";
import { Image as ImageIcon } from "lucide-react";
import { useState, useRef } from "react";

const CHAR_LIMIT = 500;

export default function PostComposer() {
  const [content, setContent] = useState("");
  const textareaRef = useRef(null);

  const charCount = Array.from(content).length;
  const isNearLimit = charCount >= CHAR_LIMIT - 40;

  const handleChange = (e) => {
    const newValue = e.target.value;

    if (Array.from(newValue).length > CHAR_LIMIT) {
      return;
    }

    setContent(newValue);

    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };
  return (
    <div className="bg-white border-2 border-cs-line rounded-3xl p-5 mb-6">
      <div className="flex items-center gap-3 border-2 border-cs-line rounded-2xl px-4 py-3">
        <div className="w-10 h-10 rounded-full bg-cs-magenta flex-shrink-0" />
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleChange}
          placeholder="Share something with your community..."
          rows={1}
          className="flex-1 outline-none text-sm text-cs-ink placeholder:text-cs-muted resize-none overflow-hidden bg-transparent"
        />
      </div>
      <div className="flex items-center justify-between mt-4">
        <button className="w-10 h-10 rounded-full border-2 border-cs-line flex items-center justify-center text-cs-muted hover:text-cs-orange hover:border-cs-orange transition-colors">
          <ImageIcon size={18} />
        </button>
        <div className="flex items-center gap-4">
          {isNearLimit && (
            <span
              className={`text-xs font-medium ${
                charCount >= CHAR_LIMIT ? "text-cs-magenta" : "text-cs-muted"
              }`}
            >
              {charCount}/{CHAR_LIMIT}
            </span>
          )}
          <motion.button
            whileTap={{ scale: 0.96 }}
            className="bg-cs-orange text-white font-bold text-sm px-6 py-2 rounded-full"
          >
            Post
          </motion.button>
        </div>
      </div>
    </div>
  );
}
