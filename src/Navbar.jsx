import React from "react";
import { Link } from "react-scroll";
import { motion } from "framer-motion";

const Navbar = () => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, ease: "easeOut" }}
      className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-[90%] md:w-[80%]
                 backdrop-blur-md bg-white/10 border border-white/20 
                 shadow-lg rounded-full px-10 py-4 flex items-center justify-between"
    >
      {/* Logo */}
      <motion.h1
        className="text-3xl font-semibold text-white tracking-wide cursor-pointer"
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 200 }}
      >
        TRAVIS<span className="text-cyan-400">AI</span>
      </motion.h1>

      {/* Nav Links */}
      <ul className="flex space-x-10 text-white text-base font-medium">
        {[
          { name: "Home", to: "hero" },
          { name: "Features", to: "features" },
          { name: "How It Works", to: "howitworks" },
          { name: "About", to: "about" },
          { name: "FAQs", to: "faqs" },
          { name: "Contact", to: "footer" },
        ].map((link, i) => (
          <motion.li
            key={i}
            whileHover={{
              scale: 1.1,
              color: "#22d3ee",
              textShadow: "0 0 10px rgba(34, 211, 238, 0.6)",
            }}
            transition={{ type: "spring", stiffness: 300 }}
            className="cursor-pointer transition-all"
          >
            <Link
              to={link.to}
              smooth={true}
              duration={700}
              offset={-100} // adjust so sections align nicely under navbar
              spy={true}
              className="hover:text-cyan-400"
            >
              {link.name}
            </Link>
          </motion.li>
        ))}
      </ul>
    </motion.nav>
  );
};

export default Navbar;
