import { useCallback, useEffect, useRef, useState } from "react";
import { FilesetResolver, PoseLandmarker } from "@mediapipe/tasks-vision";

export const usePoseDetection = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseLandmarkerRef = useRef(null);
  const animationFrameId = useRef(null);
  const [latestPose, setLatestPose] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);

  useEffect(() => {
    let canceled = false;

    const initialize = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );

        const landmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task",
          },
          runningMode: "VIDEO",
          numPoses: 1,
          minPoseDetectionConfidence: 0.5,
          minPosePresenceConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        if (!canceled) {
          poseLandmarkerRef.current = landmarker;
          setLoading(false);
        }
      } catch (e) {
        console.error("MediaPipe initialization error:", e);
        if (!canceled) {
          setError(e);
          setLoading(false);
        }
      }
    };

    initialize();

    return () => {
      canceled = true;
      if (poseLandmarkerRef.current) {
        poseLandmarkerRef.current.close();
        poseLandmarkerRef.current = null;
      }
    };
  }, []);

  const performDetectionLoop = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const landmarker = poseLandmarkerRef.current;

    if (!video || !landmarker || !cameraActive) {
      return;
    }

    if (video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      animationFrameId.current = requestAnimationFrame(performDetectionLoop);
      return;
    }

    if (canvas && (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight)) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    const now = performance.now();
    const result = landmarker.detectForVideo(video, now);

    if (result && result.landmarks && result.landmarks.length > 0) {
      const landmarks = result.landmarks[0].map((lm) => ({
        x: lm.x,
        y: lm.y,
        z: lm.z,
        visibility: lm.visibility,
      }));

      const worldLandmarks =
        result.worldLandmarks && result.worldLandmarks.length > 0
          ? result.worldLandmarks[0].map((lm) => ({
              x: lm.x,
              y: lm.y,
              z: lm.z,
              visibility: lm.visibility,
            }))
          : null;

      setLatestPose({
        timestampMs: now,
        landmarks,
        worldLandmarks,
      });
    } else {
      setLatestPose(null);
    }

    animationFrameId.current = requestAnimationFrame(performDetectionLoop);
  }, [cameraActive]);

  const startCamera = useCallback(async () => {
    if (loading || error) {
      console.warn("Cannot start camera: loading or error state");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setCameraActive(true);
        };
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError(err);
    }
  }, [loading, error]);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    if (animationFrameId.current !== null) {
      cancelAnimationFrame(animationFrameId.current);
      animationFrameId.current = null;
    }
    setCameraActive(false);
    setLatestPose(null);
  }, []);

  useEffect(() => {
    if (cameraActive && !animationFrameId.current) {
      animationFrameId.current = requestAnimationFrame(performDetectionLoop);
    }
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
        animationFrameId.current = null;
      }
    };
  }, [cameraActive, performDetectionLoop]);

  return {
    videoRef,
    canvasRef,
    startCamera,
    stopCamera,
    latestPose,
    loading,
    error,
    cameraActive,
  };
};
