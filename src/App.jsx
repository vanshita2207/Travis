import React from "react";
import Hero from "./Hero";
import FeaturesSection from "./FeaturesSection";
import HowItWorks from "./HowItWorks";
import AboutSection from "./AboutSection";
import Testimonials from "./Testimonials";
import FAQSection from "./FAQSection";
import Footer from "./Footer";
import "./index.css";

function App() {
  return (
    <div className="bg-black min-h-screen font-[Poppins]">
      <Hero />
      <FeaturesSection />
      <HowItWorks />
      <AboutSection />
      <Testimonials />
      <FAQSection />
      <Footer />
    </div>
  );
}

export default App;
