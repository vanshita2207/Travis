import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

const Login = () => {
  const [email, setEmail] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");

  const sendOtp = async () => {
    const res = await axios.post("http://localhost:5000/send-otp", { email });
    if (res.data.success) setOtpSent(true);
    else alert("Error sending OTP");
  };

  const verifyOtp = async () => {
    const res = await axios.post("http://localhost:5000/verify-otp", { email, otp });
    if (res.data.success) {
      alert("Login Successful!");
      window.location.href = "/dashboard";
    } else {
      alert("Incorrect OTP");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-black">

      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#001f35] via-black to-[#000a1a] opacity-80"></div>
      <div className="absolute w-[900px] h-[900px] bg-cyan-500/20 blur-[200px] rounded-full top-[-200px] left-[-200px]"></div>
      <div className="absolute w-[900px] h-[900px] bg-blue-600/20 blur-[200px] rounded-full bottom-[-250px] right-[-200px]"></div>

      {/* Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative w-full max-w-md p-10 rounded-2xl
        bg-black/40 backdrop-blur-2xl border border-cyan-500/20
        shadow-[0_0_25px_#00eaff50,0_0_60px_#003bff20]"
      >

        <h1 className="text-4xl font-bold text-center bg-gradient-to-r 
          from-cyan-400 to-blue-500 text-transparent bg-clip-text drop-shadow-md">
          {otpSent ? "Verify OTP" : "Login"}
        </h1>

        <p className="text-gray-300 text-center mt-2 mb-8">
          {otpSent ? "Enter the OTP sent to your email" : "Receive a secure login code"}
        </p>

        {/* EMAIL INPUT */}
        {!otpSent ? (
          <>
            <label className="text-gray-300 text-sm mb-1">Email Address</label>
            <div className="relative">
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full p-3 rounded-lg bg-black/60 border border-cyan-500/30
                text-white placeholder-gray-400 focus:border-cyan-400
                outline-none transition-all focus:shadow-[0_0_10px_#00eaff80]"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={sendOtp}
              className="w-full py-3 mt-6 text-lg font-medium rounded-lg 
              bg-gradient-to-r from-cyan-500 to-blue-600 
              hover:opacity-90 transition shadow-lg 
              shadow-cyan-500/40 border border-cyan-400/40"
            >
              Send OTP
            </motion.button>
          </>
        ) : (
          <>
            {/* OTP INPUT */}
            <label className="text-gray-300 text-sm mb-1">Enter OTP</label>
            <div className="relative">
              <input
                type="text"
                placeholder="123456"
                className="w-full p-3 rounded-lg bg-black/60 border border-cyan-500/30
                text-white placeholder-gray-400 focus:border-cyan-400
                outline-none transition-all focus:shadow-[0_0_10px_#00eaff80]"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
              />
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={verifyOtp}
              className="w-full py-3 mt-6 text-lg font-medium rounded-lg 
              bg-gradient-to-r from-green-500 to-emerald-600 
              hover:opacity-90 transition shadow-lg 
              shadow-green-500/40 border border-green-400/40"
            >
              Verify OTP
            </motion.button>

            <button
              className="w-full text-center text-gray-300 mt-4 hover:text-white transition text-sm"
              onClick={() => setOtpSent(false)}
            >
              ← Change Email
            </button>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default Login;