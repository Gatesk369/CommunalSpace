import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Heart,
  MessageCircle,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import { toggleLike } from "../api/posts";

export default function PostCard({
  id,
  authorName,
  community,
  timeAgo,
  content,
  media = [],
  likeCount = 0,
  commentCount = 0,
  isBusiness = false,
  userHasLiked = false,
}) {
  const [liked, setLiked] = useState(userHasLiked);
  const [count, setCount] = useState(likeCount);
  const [mediaIndex, setMediaIndex] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const hasMultiple = media.length > 1;

  const goNext = useCallback(
    (e) => {
      e?.stopPropagation();
      setMediaIndex((prev) => (prev + 1) % media.length);
    },
    [media.length],
  );

  const goPrev = useCallback(
    (e) => {
      e?.stopPropagation();
      setMediaIndex((prev) => (prev - 1 + media.length) % media.length);
    },
    [media.length],
  );

  useEffect(() => {
    if (!lightboxOpen) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") setLightboxOpen(false);
      if (e.key === "ArrowRight") goNext();
      if (e.key === "ArrowLeft") goPrev();
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [lightboxOpen, goNext, goPrev]);

  async function handleToggleLike() {
    const previousLiked = liked;
    const previousCount = count;

    setLiked(!liked);
    setCount(liked ? count - 1 : count + 1);

    try {
      await toggleLike(id);
    } catch {
      setLiked(previousLiked);
      setCount(previousCount);
    }
  }

  const activeMedia = media[mediaIndex];

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

      {media.length > 0 && (
        <div className="relative rounded-2xl overflow-hidden mb-2">
          <div
            onClick={() => setLightboxOpen(true)}
            className="bg-cs-line aspect-square overflow-hidden cursor-pointer"
          >
            {activeMedia.media_type === "video" ? (
              <video
                src={activeMedia.file}
                controls
                className="w-full h-full object-cover"
              />
            ) : (
              <img
                src={activeMedia.file}
                alt="Post media"
                className="w-full h-full object-cover"
              />
            )}
          </div>

          {hasMultiple && (
            <>
              <button
                onClick={goPrev}
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-1.5 hover:bg-black/70"
              >
                <ChevronLeft size={18} />
              </button>
              <button
                onClick={goNext}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-1.5 hover:bg-black/70"
              >
                <ChevronRight size={18} />
              </button>
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
                {media.map((_, i) => (
                  <button
                    key={i}
                    onClick={(e) => {
                      e.stopPropagation();
                      setMediaIndex(i);
                    }}
                    className={`w-1.5 h-1.5 rounded-full transition-colors ${
                      i === mediaIndex ? "bg-white" : "bg-white/50"
                    }`}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <p className="text-sm text-cs-ink leading-relaxed mb-4">{content}</p>

      <div className="flex items-center gap-3">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={handleToggleLike}
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

      <AnimatePresence>
        {lightboxOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLightboxOpen(false)}
            className="fixed inset-0 bg-black/90 z-[100] flex items-center justify-center p-8"
          >
            <button
              onClick={() => setLightboxOpen(false)}
              className="absolute top-6 right-6 text-white/80 hover:text-white"
            >
              <X size={28} />
            </button>

            <div
              onClick={(e) => e.stopPropagation()}
              className="relative max-w-4xl max-h-full flex items-center justify-center"
            >
              {activeMedia.media_type === "video" ? (
                <video
                  src={activeMedia.file}
                  controls
                  autoPlay
                  className="max-w-full max-h-[85vh] object-contain"
                />
              ) : (
                <img
                  src={activeMedia.file}
                  alt="Post media full view"
                  className="max-w-full max-h-[85vh] object-contain"
                />
              )}

              {hasMultiple && (
                <>
                  <button
                    onClick={goPrev}
                    className="absolute left-0 -translate-x-16 top-1/2 -translate-y-1/2 text-white/80 hover:text-white"
                  >
                    <ChevronLeft size={32} />
                  </button>
                  <button
                    onClick={goNext}
                    className="absolute right-0 translate-x-16 top-1/2 -translate-y-1/2 text-white/80 hover:text-white"
                  >
                    <ChevronRight size={32} />
                  </button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
