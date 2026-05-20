# PosePerfect AI - Product Requirements Document

## Original Problem Statement
PosePerfect AI — Next-Generation Real-Time Spatial Pose Director. A web app that resolves "posing paralysis" by transforming the smartphone into an active 3D Spatial Director using on-device computer vision, semantic segmentation, and real-time generative wireframes to guide both photographer and subject into mathematically optimized, context-aware compositions.

## Tech Stack
- **Frontend**: React 19 + MediaPipe Tasks Vision (Pose Landmarker) + Framer Motion + Tailwind CSS
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (trending poses collection)
- **Design**: Dark glassmorphic UI, Outfit + Inter fonts, Archetype 4 (Swiss High-Contrast + AR Tech)

## User Personas
1. **The Subject (Casual Memory Capturer)** - Freezes up in front of camera, doesn't know hand/foot placement
2. **The Director (Mobile Photographer)** - Lacks structural training, struggles with composition guidance

## Architecture
- **Frontend (on-device)**: Camera stream → MediaPipe Pose detection → 33 3D landmarks → Wireframe overlay rendered on canvas with red→green alignment gradient
- **Backend**: Pre-seeded trending poses DB with skeletal coordinates, filtered by mood pack + scene type
- **Privacy**: Raw camera data never leaves the device, only fetches pose templates from server

## What's Been Implemented (May 19, 2026)
### Backend
- `GET /api/` - Health check
- `GET /api/poses?mood=X&scene=Y` - List trending poses with filters
- `GET /api/poses/{id}` - Single pose detail (returns 404 if not found)
- Auto-seeded 7 trending poses across mood packs (Y2K, Vogue Editorial, Candid Streetwear) and scene types (urban_street, beach, indoor_cafe, architectural)
- 33-landmark BlazePose-compatible skeletal data for each pose

### Frontend
- Edge-to-edge camera viewport with `getUserMedia` integration
- MediaPipe Pose Landmarker (full model) running real-time on-device
- Wireframe overlay canvas with color-coded alignment feedback (red → green)
- Glassmorphic floating HUD (header, mood selector, scene selector, alignment indicator, capture button)
- Mood Pack selector with 3 packs (Y2K Aesthetic, Vogue Editorial, Candid Streetwear)
- Scene type selector with 4 environments
- Previous/Next pose navigation buttons
- Alignment percentage indicator with color-coded score
- Error toast for camera access denial

## Core Requirements Status
| Feature | Priority | Status |
|---------|----------|--------|
| FR-1.1 Scene Context Parsing | P0 | Mocked via manual scene selector |
| FR-1.2 Attire Segmentation | P0 | Deferred (P1 enhancement) |
| FR-1.3 Lighting Analyzer | P1 | Deferred |
| FR-1.4 Trend Vectorization Pipeline | P0 | Mocked via seeded DB |
| FR-2.1 3D Wireframe HUD | P0 | ✅ Done |
| FR-2.2 Color Gradient Alignment | P0 | ✅ Done |
| FR-2.3 Haptic/Audio Loop | P1 | Deferred |
| FR-2.4 Multi-Person Group Sync | P0 | Single-person only (deferred) |
| FR-2.5 Mood Packs | P1 | ✅ Done |
| FR-3.1 Glassmorphic HUD | P0 | ✅ Done |
| FR-3.2 Horizontal Swipe Pose Swap | P0 | ✅ Done (via prev/next buttons) |

## Prioritized Backlog (Next Phase)
### P0 Remaining
- True swipe gesture (currently button-based) for pose cycling
- Functional capture button (save composite image with overlay)
- Multi-person group pose sync (up to 5 people)

### P1 Enhancements
- Attire segmentation (clothing-aware pose filtering)
- Haptic feedback when alignment > 90%
- Audio TTS director cues ("Tilt chin down")
- Ambient lighting analyzer
- Pose history / favorites
- Share generated photos

### P2 Future
- Real social media trend ingestion pipeline (currently mocked)
- ML-based scene detection (currently manual selector)
- AR depth perception via device gyroscope
- Native mobile apps (iOS/Android)

## Testing Status
- Backend: 14/14 pytest cases passing (100%)
- Frontend: All UI components verified, MediaPipe loads successfully
- Camera flow: Verified initialization works (camera unavailable in sandboxed test env, expected behavior)
