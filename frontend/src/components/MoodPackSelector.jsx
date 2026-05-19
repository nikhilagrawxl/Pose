import React from "react";
import { motion } from "framer-motion";

const MOOD_PACKS = [
  { id: "Y2K Aesthetic", label: "Y2K Aesthetic", icon: "✨" },
  { id: "Vogue Editorial", label: "Vogue Editorial", icon: "👗" },
  { id: "Candid Streetwear", label: "Candid Streetwear", icon: "🎒" },
];

const MoodPackSelector = ({ selectedMood, onMoodChange }) => {
  return (
    <div
      data-testid="mood-selector-carousel"
      className="flex gap-3 overflow-x-auto scrollbar-hide px-6 py-4"
    >
      {MOOD_PACKS.map((mood) => (
        <motion.button
          key={mood.id}
          data-testid={`mood-badge-${mood.id.toLowerCase().replace(/\s+/g, "-")}`}
          onClick={() => onMoodChange(mood.id)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={
            `flex items-center gap-2 px-4 py-2 rounded-full backdrop-blur-md border text-sm font-medium whitespace-nowrap transition-all ${
              selectedMood === mood.id
                ? "bg-white/20 border-white/40 text-white"
                : "bg-white/10 border-white/20 text-white/80 hover:bg-white/15"
            }`
          }
        >
          <span>{mood.icon}</span>
          <span>{mood.label}</span>
        </motion.button>
      ))}
    </div>
  );
};

export default MoodPackSelector;
