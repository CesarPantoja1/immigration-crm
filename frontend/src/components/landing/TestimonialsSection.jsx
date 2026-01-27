export default function TestimonialsSection() {
  return (
    <section className="py-16 bg-gradient-to-r from-primary-50 to-blue-50 border-y border-primary-100">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <blockquote className="text-xl md:text-2xl text-gray-700 italic mb-6">
          "Una plataforma increíble que transformó completamente mi experiencia migratoria. Todo fue claro, rápido y sin complicaciones."
        </blockquote>
        <div className="flex items-center justify-center space-x-1 text-yellow-400 text-2xl mb-4">
          <span>★</span><span>★</span><span>★</span><span>★</span><span>★</span>
        </div>
        <p className="text-gray-500 font-medium">Miles de usuarios confían en nosotros</p>
      </div>
    </section>
  )
}
