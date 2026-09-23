# Feature: Legacy Media Forensics (Preserved from ShadowGuard)

## Metadata
- **Feature Name:** Legacy Media Forensics (Preserved from ShadowGuard)
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Legacy Archive (Post-Phase 10 Consideration)
- **Dependencies:** FFmpeg, PyTorch / OpenCV (legacy mock pipelines)

---

## 1. Description
Preserves documentation and architectural artifacts from the original ShadowGuard project concerning deepfake video and audio detection. While ALIAS is fundamentally focused on authentication telemetry and login anomaly investigation, these legacy components are documented for historical continuity and potential future multimodal identity verification modules.

---

## 2. Intended Behavior (Historical & Future Horizon)
- **Historical Behavior:** ShadowGuard provided placeholder endpoints for uploading audio/video files to run synthetic deepfake probability scoring.
- **Current State:** Completely decoupled from the primary ALIAS runtime. No mock media analysis endpoints or heavy unverified deep learning frameworks are included in the Phase 1 ALIAS engine.
- **Future Multimodal Verification (Post-Phase 10):** Should biometric or video-based step-up authentication telemetry be integrated into enterprise login pipelines, media forensic models can be reintroduced as an auxiliary detector plug-in.

---

## 3. Dependencies
- Legacy tables: `video_analysis`, `audio_analysis` (deprecated in ALIAS Phase 1)
- Future: Optional biometric media inspection microservice
