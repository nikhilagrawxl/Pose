import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, X, ChevronLeft, ChevronRight } from "lucide-react";
import { usePoseDetection } from "../hooks/usePoseDetection";
import WireframeOverlay from "../components/WireframeOverlay";
import MoodPackSelector from "../components/MoodPackSelector";
import AlignmentIndicator from "../components/AlignmentIndicator";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SCENE_TYPES = [
  { id: "urban_street", label: "Urban Street" },
  { id: "beach", label: "Beach" },
  { id: "indoor_cafe", label: "Indoor" },
  { id: "architectural", label: "Architectural" },
];

const PoseDirector = () => {
  const {
    videoRef,
    startCamera,
    stopCamera,
    latestPose,
    loading,
    error,
    cameraActive,
  } = usePoseDetection();

  const [selectedMood, setSelectedMood] = useState("Y2K Aesthetic");
  const [selectedScene, setSelectedScene] = useState("urban_street");
  const [trendingPoses, setTrendingPoses] = useState([]);
  const [currentPoseIndex, setCurrentPoseIndex] = useState(0);
  const [dimensions, setDimensions] = useState({ width: 1280, height: 720 });
  const [loadingPoses, setLoadingPoses] = useState(false);

  const fetchTrendingPoses = useCallback(async () => {
    setLoadingPoses(true);
    try {
      const response = await axios.get(`${API}/poses`, {
        params: {
          mood: selectedMood,
          scene: selectedScene,
        },
      });
      setTrendingPoses(response.data);
      setCurrentPoseIndex(0);
    } catch (err) {
      console.error("Failed to fetch trending poses:", err);
    } finally {
      setLoadingPoses(false);
    }
  }, [selectedMood, selectedScene]);

  useEffect(() => {
    fetchTrendingPoses();
  }, [fetchTrendingPoses]);

  const handleCameraToggle = () => {
    if (cameraActive) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  const handleNextPose = () => {
    if (trendingPoses.length > 0) {
      setCurrentPoseIndex((prev) => (prev + 1) % trendingPoses.length);
    }
  };

  const handlePreviousPose = () => {
    if (trendingPoses.length > 0) {
      setCurrentPoseIndex((prev) => (prev - 1 + trendingPoses.length) % trendingPoses.length);
    }
  };

  const currentReferencePose = trendingPoses[currentPoseIndex] || null;

  useEffect(() => {
    const updateDimensions = () => {
      if (videoRef.current && videoRef.current.videoWidth > 0) {
        setDimensions({
          width: videoRef.current.videoWidth,
          height: videoRef.current.videoHeight,
        });
      }
    };

    const video = videoRef.current;
    if (video) {
      video.addEventListener("loadedmetadata", updateDimensions);
      return () => video.removeEventListener("loadedmetadata", updateDimensions);
    }
  }, [videoRef]);

  return (
    <div data-testid="pose-director-page" className="relative w-full h-screen overflow-hidden bg-black">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="absolute top-0 left-0 w-full h-full object-cover"
        style={{ transform: "scaleX(-1)" }}
      />

      {!cameraActive && (
        <div 
          className="absolute top-0 left-0 w-full h-full bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1731589802956-b4693dae884b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NjV8MHwxfHNlYXJjaHwxfHxmYXNoaW9uJTIwc3RyZWV0JTIwc3R5bGUlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzkxNjU5NjV8MA&ixlib=rb-4.1.0&q=85')`,
          }}
        />
      )}

      {cameraActive && latestPose && (
        <WireframeOverlay
          userPose={latestPose}
          referencePose={currentReferencePose}
          dimensions={dimensions}
        />
      )}

      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="relative w-full h-full flex flex-col justify-between pointer-events-none">
          <div className="pointer-events-auto">
            <div className="pt-6 px-6">
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="backdrop-blur-2xl bg-black/40 border border-white/15 rounded-3xl px-6 py-4 shadow-2xl inline-block"
              >
                <h1 className="text-2xl font-semibold tracking-tighter text-white">
                  PosePerfect AI
                </h1>
                <p className="text-sm text-zinc-400 mt-1">
                  Real-Time Spatial Pose Director
                </p>
              </motion.div>
            </div>

            <div className="mt-4">
              <MoodPackSelector
                selectedMood={selectedMood}
                onMoodChange={setSelectedMood}
              />
            </div>

            <div className="mt-3 px-6">
              <div className="flex gap-2">
                {SCENE_TYPES.map((scene) => (
                  <motion.button
                    key={scene.id}
                    data-testid={`scene-selector-${scene.id}`}
                    onClick={() => setSelectedScene(scene.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={
                      `px-3 py-1 rounded-full backdrop-blur-md border text-xs font-medium transition-all ${
                        selectedScene === scene.id
                          ? "bg-white/20 border-white/40 text-white"
                          : "bg-white/10 border-white/20 text-white/70 hover:bg-white/15"
                      }`
                    }
                  >
                    {scene.label}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>

          <div className="pointer-events-auto pb-8">
            {cameraActive && currentReferencePose && (
              <div className="flex justify-between items-end px-6">
                <div className="flex flex-col gap-4">
                  <AlignmentIndicator
                    userPose={latestPose}
                    referencePose={currentReferencePose}
                  />
                  
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="backdrop-blur-2xl bg-black/40 border border-white/15 rounded-3xl px-4 py-3 shadow-2xl"
                  >
                    <div className="text-xs font-semibold uppercase tracking-[0.2em] text-zinc-400">
                      Current Pose
                    </div>
                    <div className="text-lg font-medium text-white mt-1">
                      {currentReferencePose.name}
                    </div>
                  </motion.div>
                </div>

                <div className="flex flex-col gap-3 items-center">
                  <motion.button
                    data-testid="pose-swipe-previous"
                    onClick={handlePreviousPose}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="w-12 h-12 rounded-full backdrop-blur-md bg-white/10 border border-white/20 flex items-center justify-center text-white hover:bg-white/20 transition-all"
                  >
                    <ChevronLeft size={24} />
                  </motion.button>

                  <motion.button
                    data-testid="capture-button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-20 h-20 rounded-full border-4 border-white/50 flex items-center justify-center bg-transparent transition-transform"
                  >
                    <div className="w-16 h-16 rounded-full bg-white transition-colors" />
                  </motion.button>

                  <motion.button
                    data-testid="pose-swipe-next"
                    onClick={handleNextPose}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="w-12 h-12 rounded-full backdrop-blur-md bg-white/10 border border-white/20 flex items-center justify-center text-white hover:bg-white/20 transition-all"
                  >
                    <ChevronRight size={24} />
                  </motion.button>
                </div>
              </div>
            )}

            {!cameraActive && (
              <div className="flex justify-center">
                <motion.button
                  data-testid="start-camera-button"
                  onClick={handleCameraToggle}
                  disabled={loading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="backdrop-blur-2xl bg-white/10 border border-white/30 rounded-full px-8 py-4 text-white font-medium text-lg shadow-2xl hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
                >
                  <Camera size={24} />
                  {loading ? "Loading MediaPipe..." : "Start Camera"}
                </motion.button>
              </div>
            )}

            {cameraActive && !currentReferencePose && (
              <div className="flex justify-center">
                <motion.button
                  data-testid="stop-camera-button"
                  onClick={handleCameraToggle}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="backdrop-blur-2xl bg-red-500/20 border border-red-500/30 rounded-full px-8 py-4 text-white font-medium text-lg shadow-2xl hover:bg-red-500/30 transition-all flex items-center gap-3"
                >
                  <X size={24} />
                  Stop Camera
                </motion.button>
              </div>
            )}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            data-testid="error-toast"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="absolute top-6 left-1/2 transform -translate-x-1/2 backdrop-blur-2xl bg-red-500/20 border border-red-500/30 rounded-2xl px-6 py-3 text-white shadow-2xl z-50"
          >
            <div className="text-sm font-medium">
              Error: {error.message || "Camera access denied"}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {loadingPoses && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full"
          />
        </div>
      )}
    </div>
  );
};

export default PoseDirector;
