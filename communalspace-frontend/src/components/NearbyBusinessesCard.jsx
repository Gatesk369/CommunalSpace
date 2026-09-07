import { useState } from "react";
import { motion } from "motion/react";

function BusinessRow({ name, initiallyFollowing = false }) {
  const [following, setFollowing] = useState(initiallyFollowing);
  return (
    <div className="flex items-center gap-3 py-3 border-b border-cs-line last:border-b-0">
      <div className="w-9 h-9 rounded-xl bg-cs-line flex-shrink-0" />
      <span className="flex-1 text-sm font-semibold text-cs-ink truncate">
        {name}
      </span>
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={() => setFollowing((f) => !f)}
        className={`text-xs font-bold px-3 py-1.5 rounded-full flex-shrink-0 ${
          following
            ? "bg-[linear-gradient(120deg,theme(colors.cs-red),theme(colors.cs-purple))] text-white"
            : "border-2 border-cs-line text-cs-ink"
        }`}
      >
        {following ? "Following" : "Follow"}
      </motion.button>
    </div>
  );
}

export default function NearbyBusinessesCard({ businesses }) {
  return (
    <div className="bg-white border-2 border-cs-line rounded-3xl p-5 mb-6">
      <h2 className="text-base font-bold text-cs-ink mb-1">
        Nearby Businesses
      </h2>
      <div>
        {businesses.map((b) => (
          <BusinessRow key={b.name} {...b} />
        ))}
      </div>
    </div>
  );
}
