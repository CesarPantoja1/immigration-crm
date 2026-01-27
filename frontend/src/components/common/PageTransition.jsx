import { motion } from 'framer-motion'

const pageVariants = {
  initial: {
    opacity: 0,
    x: 60
  },
  in: {
    opacity: 1,
    x: 0
  },
  out: {
    opacity: 0,
    x: -60
  }
}

const pageTransition = {
  type: 'spring',
  stiffness: 300,
  damping: 30
}

export default function PageTransition({ children }) {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      className="h-full w-full"
    >
      {children}
    </motion.div>
  )
}
