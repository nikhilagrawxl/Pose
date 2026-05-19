import React, { useEffect, useRef } from "react";

const POSE_CONNECTIONS = [
  [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
  [11, 23], [12, 24], [23, 24],
  [23, 25], [25, 27], [27, 29], [27, 31],
  [24, 26], [26, 28], [28, 30], [28, 32],
];

const WireframeOverlay = ({ userPose, referencePose, dimensions }) => {
  const canvasRef = useRef(null);

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

  const getColorForAlignment = (score) => {
    const red = Math.round(255 * (1 - score / 100));
    const green = Math.round(255 * (score / 100));
    return `rgb(${red}, ${green}, 20)`;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !dimensions) return;

    const ctx = canvas.getContext("2d");
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const drawPose = (landmarks, color, lineWidth) => {
      if (!landmarks || landmarks.length === 0) return;

      const toPixel = (lm) => ({
        x: lm.x * canvas.width,
        y: lm.y * canvas.height,
      });

      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;

      POSE_CONNECTIONS.forEach(([i, j]) => {
        if (landmarks[i] && landmarks[j] && 
            landmarks[i].visibility > 0.5 && landmarks[j].visibility > 0.5) {
          const a = toPixel(landmarks[i]);
          const b = toPixel(landmarks[j]);
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      });

      ctx.fillStyle = color;
      landmarks.forEach((lm) => {
        if (lm.visibility > 0.5) {
          const p = toPixel(lm);
          ctx.beginPath();
          ctx.arc(p.x, p.y, 4, 0, 2 * Math.PI);
          ctx.fill();
        }
      });
    };

    if (referencePose && referencePose.landmarks) {
      drawPose(referencePose.landmarks, "rgba(10, 132, 255, 0.6)", 3);
    }

    if (userPose && userPose.landmarks) {
      const alignment = referencePose 
        ? calculateAlignment(userPose.landmarks, referencePose.landmarks)
        : 0;
      const color = referencePose ? getColorForAlignment(alignment) : "rgba(255, 255, 255, 0.8)";
      drawPose(userPose.landmarks, color, 4);
    }
  }, [userPose, referencePose, dimensions]);

  return (
    <canvas
      ref={canvasRef}
      data-testid="wireframe-overlay-canvas"
      className="absolute top-0 left-0 w-full h-full pointer-events-none"
      style={{ zIndex: 10 }}
    />
  );
};

export default WireframeOverlay;
