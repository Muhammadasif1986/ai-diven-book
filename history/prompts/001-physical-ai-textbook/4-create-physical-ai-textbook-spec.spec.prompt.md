---
id: 4
title: Create Physical AI Textbook Spec
stage: spec
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: physical-ai-textbook
branch: 001-physical-ai-textbook
user: unknown
command: /sp.specify Physical AI & Humanoid Robotics Textbook ...
labels: ["spec-creation"]
links:
  spec: specs/001-physical-ai-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-physical-ai-textbook/spec.md
  - specs/001-physical-ai-textbook/checklists/requirements.md
tests:
  - null
---

## Prompt

```text
Physical AI & Humanoid Robotics Textbook

Project Summary:
Develop an academically rigorous, AI-native textbook titled
"Physical AI & Humanoid Robotics: Bridging the Digital Brain and the Physical World."
The book will be written in Docusaurus-ready Markdown, built with Spec-Kit Plus,
and deployed via GitHub Pages using Claude Code CLI with MCP servers (Context7 & GitHub).

Target Audience:
Undergraduate and graduate students in Computer Science, Robotics, and AI engineering.
Secondary audience: educators designing Physical AI or Humanoid Robotics curricula.

Focus and Theme:
Physical AI, Embodied Intelligence, Humanoid Robotics, and AI systems operating in physical environments.
Core theme: Bridging the gap between digital AI models and real-world robotic embodiment.

Goal:
Enable students to design, simulate, and deploy humanoid robots in both simulated and real-world environments.
Teach practical skills in ROS 2, Gazebo, Unity, and NVIDIA Isaac Sim, while connecting these systems to
LLMs, Vision-Language-Action (VLA) models, and Edge AI devices (Jetson).

Scope:
The textbook covers the following modules:

Module 1 — The Robotic Nervous System (ROS 2)
- ROS 2 nodes, topics, services, actions
- Building Python ROS 2 packages with rclpy
- URDF for humanoid robots

Module 2 — The Digital Twin (Gazebo + Unity)
- Physics simulation, collisions, and sensor simulation
- Gazebo for robotics; Unity for high-fidelity HRI simulation
- Simulated sensors: LiDAR, depth cameras, IMUs

Module 3 — The AI-Robot Brain (NVIDIA Isaac)
- Isaac Sim for synthetic data generation
- Isaac ROS for hardware-accelerated VSLAM
- Nav2 path-planning for bipedal movement

Module 4 — Vision-Language-Action (VLA)
- Voice-to-Action with Whisper
- Cognitive planning using LLMs → ROS 2 action pipelines
- Capstone project: Autonomous Humanoid executing spoken tasks

Why Physical AI Matters:
Humanoid robots excel because they share human form factors, making them compatible with
existing environments. Physical AI marks the transition from digital AI to embodied intelligence.

Learning Outcomes:
- Understand embodied intelligence & Physical AI principles
- Master ROS 2 for robotic control
- Build simulations with Gazebo/Unity
- Use NVIDIA Isaac for perception & simulation
- Integrate GPT/VLA models into robotics systems
- Design humanoid robot movement, interaction, and cognition

Weekly Breakdown:
Weeks 1–2: Intro to Physical AI & embodied intelligence
Weeks 3–5: ROS 2 fundamentals
Weeks 6–7: Gazebo/Unity simulation
Weeks 8–10: NVIDIA Isaac platform
Weeks 11–12: Humanoid kinematics, dynamics, locomotion
Week 13: Conversational Robotics & VLA

Assessments:
- ROS 2 package development
- Gazebo simulation project
- Isaac-based perception pipeline
- Capstone: Simulated humanoid robot with conversational AI

Hardware Specifications:
- Workstation: RTX 4070 Ti+ (ideal: RTX 3090/4090), 64GB RAM, Ubuntu 22.04
- Edge AI Kit: Jetson Orin Nano/NX, RealSense D435i, IMU, microphone array
- Robotics Options: Unitree Go2, Unitree G1 humanoid, Hiwonder TonyPi Pro, Robotis OP3
- Cloud Option: AWS g5/g6e GPU instances with Omniverse Isaac Sim

Architecture Summary:
- Sim Rig handles Isaac Sim, Gazebo, Unity
- Jetson acts as inference and control brain
- Sensors feed real-time perception data
- Robot executes motor commands and physical tasks

Success Criteria:
- Produces 5,000–7,000 words of original academic content
- Minimum 15 academic sources, APA formatted
- At least 50% peer-reviewed robotics/AI papers
- Zero plagiarism and all claims sourced
- Fully builds and renders in Docusaurus using Context7 MCP
- Deploys successfully to GitHub Pages via Claude Code MCP GitHub server
- Generates a PDF export (with citations embedded)

Constraints:
- Format: Docusaurus Markdown + APA citations
- Must follow Docusaurus documentation at https://context7.com/websites/docusaurus_io
- Outputs must be compatible with Spec-Kit Plus workflow
- Writing level: Flesch-Kincaid grade 10–12
- Timeline: Deliver in structured increments (chapters/modules)

Not Building:
- Full robotics hardware build instructions
- A robotics programming bootcamp or coding tutorial
- An ethics deep-dive (separate course)
- Vendor comparisons (Unitree vs Boston Dynamics, etc.)

Primary Deliverables:
1. Docusaurus-ready textbook content with chapters matching modules
2. Citations, bibliography, figures descriptions, and diagrams (text-based for now)
3. Final compiled PDF
4. GitHub Pages deployment structure
5. Capstone project description + workflow

```

## Response snapshot

The feature specification for "Physical AI & Humanoid Robotics Textbook" at `specs/001-physical-ai-textbook/spec.md` has been successfully created and passed all quality checks. The edge cases were updated as well. The specification is now ready for the planning phase. You can proceed with `/sp.plan`.

## Outcome

- ✅ Impact: Feature specification created and validated.
- 🧪 Tests: N/A
- 📁 Files: 2 files created/updated: specs/001-physical-ai-textbook/spec.md, specs/001-physical-ai-textbook/checklists/requirements.md
- 🔁 Next prompts: Proceed with /sp.plan.
- 🧠 Reflection: Successfully created the spec and updated the checklist and PHR.

## Evaluation notes (flywheel)

- Failure modes observed: Initial write failure due to perceived unread file. This was resolved by attempting the write again after a read.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ensure consistency in tool state perception for consecutive read/write operations.
