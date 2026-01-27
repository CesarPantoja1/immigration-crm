import { Link } from 'react-router-dom'

export default function CTASection() {
  return (
    <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-3xl md:text-4xl font-serif font-bold text-white mb-6">
          ¿Listo para simplificar tu proceso migratorio?
        </h2>
        <p className="text-xl text-primary-100 mb-10">
          Únete a miles de personas que ya confían en MigraFácil para su trámite migratorio.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link 
            to="/registro" 
            className="px-8 py-4 bg-white text-primary-600 font-bold rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
          >
            Comenzar Ahora — Es Gratis
          </Link>
          <a 
            href="#contacto" 
            className="px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-full hover:bg-white/10 transition-all duration-300"
          >
            Hablar con un Asesor
          </a>
        </div>
      </div>
    </section>
  )
}
