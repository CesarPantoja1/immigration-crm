import { Link } from 'react-router-dom'
import Header from '../components/landing/Header'
import HeroSection from '../components/landing/HeroSection'
import StatsSection from '../components/landing/StatsSection'
import TestimonialsSection from '../components/landing/TestimonialsSection'
import ServicesSection from '../components/landing/ServicesSection'
import HowItWorksSection from '../components/landing/HowItWorksSection'
import FeaturesSection from '../components/landing/FeaturesSection'
import CTASection from '../components/landing/CTASection'
import ContactSection from '../components/landing/ContactSection'
import Footer from '../components/landing/Footer'

export default function LandingPage() {
  return (
    <div className="font-sans antialiased">
      <Header />
      
      <main className="pt-20">
        <HeroSection />
        <StatsSection />
        <TestimonialsSection />
        <ServicesSection />
        <HowItWorksSection />
        <FeaturesSection />
        <CTASection />
        <ContactSection />
      </main>
      
      <Footer />
    </div>
  )
}
