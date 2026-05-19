import React from "react";
import { motion } from "framer-motion";

const calculateAlignment = (userLandmarks, refLandmarks) => {
  if (!userLandmarks || !refLandmarks || userLandmarks.length !== refLandmarks.length) {
    return 0;
  }

  let totalDistance = 0;
  let count = 0;

  for (let i = 0; i < userLandmarks.length; i++) {
    const user = userLandmarks[i];
    const ref = refLandmarks[i];
    
    if (user.visibility > 0.5 && ref.visibility > 0.5) {
      const dx = user.x - ref.x;
      const dy = user.y - ref.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      totalDistance += distance;
      count++;
    }
  }

  if (count === 0) return 0;
  
  const avgDistance = totalDistance / count;
  const alignmentScore = Math.max(0, Math.min(100, (1 - avgDistance * 5) * 100));
  return Math.round(alignmentScore);
};

const AlignmentIndicator = ({ userPose, referencePose }) => {
  const alignment = userPose && referencePose
    ? calculateAlignment(userPose.landmarks, referencePose.landmarks)
    : 0;

  const getColorClass = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 50) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <motion.div
      data-testid="alignment-percentage-indicator"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="backdrop-blur-2xl bg-black/40 border border-white/15 rounded-3xl px-6 py-4 shadow-2xl"
    >
      <div className="text-center">
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-zinc-400 mb-1">
          Alignment
        </div>
        <div className={`text-5xl font-semibold tracking-tighter ${getColorClass(alignment)}`}>
          {alignment}%
        </div>
      </div>
    </motion.div>
  );
};

export default AlignmentIndicator;
