import { motion } from "motion/react";
import { Image as ImageIcon, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { createPost } from "../api/posts";

const CHAR_LIMIT = 500;
const MAX_MEDIA = 4;

export default function PostComposer({ onPostCreated }) {
  const [content, setContent] = useState("");
  const [mediaFiles, setMediaFiles] = useState([]);
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const charCount = Array.from(content).length;
  const isNearLimit = charCount >= CHAR_LIMIT - 40;

  useEffect(() => {
    return () => {
      mediaFiles.forEach((m) => URL.revokeObjectURL(m.previewUrl));
    };
  }, [mediaFiles]);

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

  function handleFileSelect(e) {
    const selected = Array.from(e.target.files);
    const room = MAX_MEDIA - mediaFiles.length;

    if (room <= 0) {
      setError(`You can only attach up to ${MAX_MEDIA} media items.`);
      e.target.value = "";
      return;
    }

    const toAdd = selected.slice(0, room);
    setError(
      selected.length > room
        ? `Only ${room} more item(s) could be added (max ${MAX_MEDIA}).`
        : "",
    );

    const newItems = toAdd.map((file) => ({
      file,
      previewUrl: URL.createObjectURL(file),
      isVideo: file.type.startsWith("video/"),
    }));

    setMediaFiles((prev) => [...prev, ...newItems]);
    e.target.value = "";
  }

  function removeMedia(index) {
    setMediaFiles((prev) => {
      const target = prev[index];
      if (target) URL.revokeObjectURL(target.previewUrl);
      return prev.filter((_, i) => i !== index);
    });
  }

  async function handleSubmit() {
    if ((!content.trim() && mediaFiles.length === 0) || posting) return;

    setPosting(true);
    setError("");

    try {
      const newPost = await createPost({
        content,
        media: mediaFiles.map((m) => m.file),
      });
      setContent("");
      mediaFiles.forEach((m) => URL.revokeObjectURL(m.previewUrl));
      setMediaFiles([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
      onPostCreated?.(newPost);
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

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

      {mediaFiles.length > 0 && (
        <div className="flex gap-3 mt-4 flex-wrap">
          {mediaFiles.map((m, index) => (
            <div
              key={m.previewUrl}
              className="relative w-24 h-24 rounded-xl overflow-hidden border-2 border-cs-line"
            >
              {m.isVideo ? (
                <video
                  src={m.previewUrl}
                  className="w-full h-full object-cover"
                />
              ) : (
                <img
                  src={m.previewUrl}
                  alt="Attached media preview"
                  className="w-full h-full object-cover"
                />
              )}
              <button
                onClick={() => removeMedia(index)}
                className="absolute top-1 right-1 bg-black/60 text-white rounded-full p-1 hover:bg-black/80"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {error && <p className="text-xs text-cs-red mt-2">{error}</p>}

      <div className="flex items-center justify-between mt-4">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,video/*"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={mediaFiles.length >= MAX_MEDIA}
          className="w-10 h-10 rounded-full border-2 border-cs-line flex items-center justify-center text-cs-muted hover:text-cs-orange hover:border-cs-orange transition-colors disabled:opacity-40"
        >
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
            onClick={handleSubmit}
            disabled={posting || (!content.trim() && mediaFiles.length === 0)}
            className="bg-cs-orange text-white font-bold text-sm px-6 py-2 rounded-full disabled:opacity-50"
          >
            {posting ? "Posting..." : "Post"}
          </motion.button>
        </div>
      </div>
    </div>
  );
}
