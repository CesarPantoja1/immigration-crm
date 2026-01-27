export default function StatsSection() {
  const stats = [
    { value: '30%', label: 'Menos tiempo de procesamiento' },
    { value: '24/7', label: 'Seguimiento disponible' },
    { value: '100%', label: 'Digital y seguro' },
    { value: 'IA', label: 'Preparación inteligente' },
  ]

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-primary-600 mb-2">
                {stat.value}
              </div>
              <p className="text-gray-600">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
