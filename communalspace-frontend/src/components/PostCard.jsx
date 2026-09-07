import { useState } from "react";
import { motion } from "motion/react";
import { Heart, MessageCircle } from "lucide-react";

export default function PostCard({
  authorName,
  community,
  timeAgo,
  content,
  likeCount = 0,
  commentCount = 0,
  isBusiness = false,
}) {
  const [liked, setLiked] = useState(false);
  const [count, setCount] = useState(likeCount);

  function toggleLike() {
    setLiked((prev) => !prev);
    setCount((prev) => (liked ? prev - 1 : prev + 1));
  }

  return (
    <div className="bg-white border-2 border-cs-line rounded-3xl p-5 mb-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-11 h-11 rounded-full bg-cs-magenta flex-shrink-0" />
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm text-cs-ink">{authorName}</span>
            {isBusiness && (
              <span className="text-[10px] font-extrabold uppercase tracking-wide bg-[linear-gradient(120deg,theme(colors.cs-magenta),theme(colors.cs-purple))] text-white px-2 py-0.5 rounded-full">
                Business
              </span>
            )}
          </div>
          <span className="text-xs text-cs-muted">
            {community} · {timeAgo}
          </span>
        </div>
      </div>

      <p className="text-sm text-cs-ink leading-relaxed mb-4">{content}</p>

      <div className="flex items-center gap-3">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={toggleLike}
          className={`flex items-center gap-1.5 border-2 rounded-full px-4 py-1.5 text-sm font-semibold transition-colors ${
            liked
              ? "border-cs-red text-cs-red bg-cs-red/5"
              : "border-cs-line text-cs-muted"
          }`}
        >
          <Heart size={15} fill={liked ? "currentColor" : "none"} />
          {count}
        </motion.button>
        <button className="flex items-center gap-1.5 border-2 border-cs-line rounded-full px-4 py-1.5 text-sm font-semibold text-cs-muted">
          <MessageCircle size={15} />
          {commentCount}
        </button>
      </div>
    </div>
  );
}
