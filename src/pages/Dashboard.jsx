import React, { useState } from "react";
import { motion } from "framer-motion";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

// Simple glowing roundabout model
function RoundaboutModel() {
  return (
    <mesh rotation={[0, 0, 0]}>
      <torusGeometry args={[2, 0.4, 16, 120]} />
      <meshStandardMaterial
        color="#00eaff"
        metalness={0.9}
        roughness={0.15}
        emissive={"#00ccff"}
        emissiveIntensity={0.4}
      />
    </mesh>
  );
}

export default function Dashboard() {
  const [videoSrc, setVideoSrc] = useState("http://localhost:5000/video-stream");

  const handleVideoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setVideoSrc(url);
    }
  };

  return (
    <div className="min-h-screen w-full bg-black text-white overflow-x-hidden">

      {/* TOP NAV */}
      <div className="w-full p-6 flex justify-between items-center bg-black/40 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50 shadow-lg">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent drop-shadow-md">
          TRAVIS Control Center
        </h1>

        <button
          onClick={() => (window.location.href = "/login")}
          className="px-6 py-2 bg-red-500/80 hover:bg-red-600 transition rounded-lg shadow-lg"
        >
          Logout
        </button>
      </div>

      {/* BACKGROUND EFFECTS */}
      <div className="absolute w-[700px] h-[700px] bg-cyan-500/20 blur-[200px] rounded-full top-[-200px] left-[-200px] pointer-events-none"></div>
      <div className="absolute w-[800px] h-[800px] bg-blue-700/20 blur-[220px] rounded-full bottom-[-250px] right-[-200px] pointer-events-none"></div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 p-8">

        {/* LEFT SIDE */}
        <div className="space-y-6 col-span-2">

          {/* REAL-TIME MODEL */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-white/10 border border-white/20 rounded-2xl backdrop-blur-xl shadow-[0_0_40px_#00eaff50]"
          >
            <h2 className="text-2xl font-semibold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Real-Time Traffic Congestion Detection
            </h2>

            {/* UPLOAD BUTTON */}
            <div className="mb-4">
              <label className="px-4 py-2 bg-cyan-500/30 hover:bg-cyan-500/50 transition rounded-lg cursor-pointer shadow-md">
                Upload Video
                <input type="file" accept="video/*" className="hidden" onChange={handleVideoUpload} />
              </label>
            </div>

            <div className="w-full h-[380px] bg-black/40 rounded-xl border border-cyan-500/30 flex items-center justify-center shadow-inner">
              <video
                src={videoSrc}
                controls
                autoPlay
                muted
                className="w-full h-full rounded-xl object-cover"
              />
            </div>
          </motion.div>

          {/* TIMELINE FULL WIDTH */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 bg-white/10 border border-white/20 rounded-2xl backdrop-blur-xl shadow-[0_0_25px_#ffffff10] w-full"
          >
            <h2 className="text-2xl font-semibold mb-6 bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              Traffic Timeline
            </h2>

            <div className="relative border-l-2 border-cyan-500/40 pl-8 space-y-10 w-full">
              {[ 
                { time: "Now", event: "Heavy congestion detected at Sector-22", color: "cyan" },
                { time: "Next 5 min", event: "Possible slowdown near City Mall junction", color: "purple" },
                { time: "Next 15 min", event: "Predicted bottleneck forming at Airport Road", color: "pink" },
                { time: "Next 30 min", event: "Construction area delay expected", color: "yellow" },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.2 }}
                  className="relative"
                >
                  <span className={`absolute -left-4 top-1 w-3 h-3 rounded-full bg-${item.color}-400`}></span>
                  <p className="text-sm text-gray-400">{item.time}</p>
                  <p className="text-lg font-semibold text-gray-100">{item.event}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

        </div>

        {/* RIGHT SIDE */}
        <div className="space-y-6">

          {/* 3D ROUNDABOUT */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-6 bg-white/10 border border-white/20 rounded-2xl backdrop-blur-xl shadow-[0_0_40px_#003bff40]"
          >
            <h2 className="text-2xl font-semibold mb-4 text-blue-400 drop-shadow-md">
              3D Roundabout Simulation
            </h2>

            <div className="w-full h-[380px] rounded-xl bg-black/40 border border-blue-500/30 shadow-inner overflow-hidden">
              <Canvas camera={{ position: [5, 5, 5] }}>
                <ambientLight intensity={1.4} />
                <OrbitControls enableZoom enablePan enableRotate />
                <RoundaboutModel />
              </Canvas>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
