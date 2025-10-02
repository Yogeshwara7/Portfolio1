"use client"

import { useEffect, useRef, useState } from "react"

interface InteractiveTechStackProps {
  className?: string
  spreadContainerRef?: React.RefObject<HTMLDivElement>
}

export default function InteractiveTechStack({ className = "", spreadContainerRef }: InteractiveTechStackProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const activeAreaRef = useRef<HTMLDivElement>(null)
  const [isHovered, setIsHovered] = useState(false)
  const [isDismantled, setIsDismantled] = useState(false)
  const techRefs = useRef<(HTMLSpanElement | null)[]>([])
  const overlayLayerRef = useRef<HTMLDivElement | null>(null)
  const animationStateRef = useRef<{
    nodes: HTMLSpanElement[]
    velocities: { x: number; y: number }[]
    rafId: number | null
    originals: { parent: Node; nextSibling: ChildNode | null; targetX: number; targetY: number; placeholder?: HTMLElement }[]
  }>({ nodes: [], velocities: [], rafId: null, originals: [] })
  const restoringRef = useRef(false)
  const outsideTimerRef = useRef<number | null>(null)
  const isPointerInsideRef = useRef(true)
  const nodeSizesRef = useRef<{ w: number; h: number }[]>([])
  const containerSizeRef = useRef<{ w: number; h: number }>({ w: 0, h: 0 })

  const frontendTechs = [
    "HTML", "CSS", "JavaScript", "React", "Next.js", "TailwindCSS", "Shadcn", "TypeScript"
  ]

  const backendTechs = [
    "Node.js", "Express.js", "MongoDB", "Google Vertex AI", "Java", "Solidity", "Firebase", "Figma"
  ]

  const toolsTechs = [
    "Git", "GitHub", "Postman", "Docker", "GCP", "Vercel", "Netlify", "Ganache", "Hardhat", "Remix"
  ]

  const allTechs = [...frontendTechs, ...backendTechs, ...toolsTechs]

  useEffect(() => {
    if (!isDismantled) return

    const container = spreadContainerRef?.current ?? (containerRef.current?.parentElement as HTMLDivElement | null)
    if (!container) return

    // Create or reuse overlay layer
    if (!overlayLayerRef.current) {
      const layer = document.createElement('div')
      layer.style.position = 'absolute'
      layer.style.inset = '0'
      layer.style.pointerEvents = 'none'
      layer.style.zIndex = '30'
      container.appendChild(layer)
      overlayLayerRef.current = layer
    }

    const layer = overlayLayerRef.current
    const state = animationStateRef.current

    // Move original nodes into the overlay and initialize physics
    let startRequested = false
    if (state.nodes.length === 0) {
      const r = container.getBoundingClientRect()
      containerSizeRef.current = { w: r.width, h: r.height }

      const allNodes = techRefs.current.filter(Boolean) as HTMLSpanElement[]
      allNodes.forEach((node, idx) => {
        // remember placement
        // capture current screen position before moving
        const rect = node.getBoundingClientRect()
        const x = rect.left - r.left + rect.width / 2
        const y = rect.top - r.top + rect.height / 2
        const parentNode = node.parentNode as Node
        const nextSibling = node.nextSibling as ChildNode | null
        // create placeholder to keep layout stable
        const placeholder = document.createElement('span')
        const cs = window.getComputedStyle(node)
        placeholder.style.display = 'inline-block'
        placeholder.style.width = `${rect.width}px`
        placeholder.style.height = `${rect.height}px`
        placeholder.style.marginTop = cs.marginTop
        placeholder.style.marginBottom = cs.marginBottom
        placeholder.style.marginLeft = cs.marginLeft
        placeholder.style.marginRight = cs.marginRight
        placeholder.style.borderRadius = cs.borderRadius
        placeholder.style.visibility = 'hidden'
        // insert placeholder exactly where node is
        if (node.parentNode) node.parentNode.insertBefore(placeholder, node)
        state.originals[idx] = { parent: parentNode, nextSibling, targetX: x, targetY: y, placeholder }

        // move into overlay layer
        layer!.appendChild(node)
        node.style.position = 'absolute'
        node.style.transition = 'none'
        node.style.left = `${x}px`
        node.style.top = `${y}px`
        node.style.transform = 'translate(-50%, -50%)'
        node.style.pointerEvents = 'none'
        node.style.whiteSpace = 'nowrap'
        node.style.willChange = 'left, top, transform'
        node.dataset.x = `${x}`
        node.dataset.y = `${y}`

        // give initial radial velocity away from container center
        const cX = containerSizeRef.current.w / 2
        const cY = containerSizeRef.current.h / 2
        const dirX = (x - cX)
        const dirY = (y - cY)
        const len = Math.hypot(dirX, dirY) || 1
        const nx = dirX / len
        const ny = dirY / len
        const speed = 1.0 + Math.random() * 1.1
        state.velocities[idx] = { x: nx * speed, y: ny * speed }
        state.nodes.push(node)

        // cache size once
        nodeSizesRef.current[idx] = { w: node.offsetWidth, h: node.offsetHeight }
      })

      // observe container resize to update cached size
      try {
        const ro = new ResizeObserver(() => {
          const b = container.getBoundingClientRect()
          containerSizeRef.current = { w: b.width, h: b.height }
        })
        ro.observe(container)
        // store observer on layer for cleanup
        ;(overlayLayerRef.current as any).__ro = ro
      } catch {}
      // request starting physics; will start after animate is defined below
      startRequested = true
    }

    let mouseX = -9999
    let mouseY = -9999
    const onMouseMove = (e: MouseEvent) => {
      const b = container.getBoundingClientRect()
      mouseX = e.clientX - b.left
      mouseY = e.clientY - b.top
    }
    window.addEventListener('mousemove', onMouseMove)

    // start a 5s timer when pointer is outside the tech stack; cancel if re-enters
    const onGlobalMove = (e: MouseEvent) => {
      if (restoringRef.current) return
      const stackRect = activeAreaRef.current?.getBoundingClientRect()
      if (!stackRect) return
      const inside =
        e.clientX >= stackRect.left &&
        e.clientX <= stackRect.right &&
        e.clientY >= stackRect.top &&
        e.clientY <= stackRect.bottom
      isPointerInsideRef.current = inside
      if (!inside) {
        if (outsideTimerRef.current == null) {
          outsideTimerRef.current = window.setTimeout(() => {
            if (!isPointerInsideRef.current) {
              restoringRef.current = true
              performRestore(true)
            }
            if (outsideTimerRef.current != null) {
              clearTimeout(outsideTimerRef.current)
              outsideTimerRef.current = null
            }
          }, 5000)
        }
    } else {
        if (outsideTimerRef.current != null) {
          clearTimeout(outsideTimerRef.current)
          outsideTimerRef.current = null
        }
        restoringRef.current = false
      }
    }
    window.addEventListener('mousemove', onGlobalMove)
    const onBlur = () => {
      // on window blur, behave like outside for 5s flow
      isPointerInsideRef.current = false
      if (outsideTimerRef.current == null) {
        outsideTimerRef.current = window.setTimeout(() => {
          if (!isPointerInsideRef.current) {
            restoringRef.current = true
            performRestore(true)
          }
          if (outsideTimerRef.current != null) {
            clearTimeout(outsideTimerRef.current)
            outsideTimerRef.current = null
          }
        }, 5000)
      }
    }
    window.addEventListener('blur', onBlur)

    const friction = 0.992
    const bounce = 0.9
    const repelRadius = 110
    const repelStrength = 220

    const animate = () => {
      const b = containerSizeRef.current
      state.nodes.forEach((node, i) => {
        const velocity = state.velocities[i]
        const size = nodeSizesRef.current[i] || { w: node.offsetWidth, h: node.offsetHeight }
        const width = size.w
        const height = size.h

        let x = parseFloat(node.dataset.x || `${Math.random() * b.w}`)
        let y = parseFloat(node.dataset.y || `${Math.random() * b.h}`)

        // mouse repulsion
        if (mouseX > 0 && mouseY > 0) {
          const dx = x - mouseX
          const dy = y - mouseY
          const dist = Math.hypot(dx, dy)
          if (dist < repelRadius && dist > 0.001) {
            const force = (repelStrength * (repelRadius - dist)) / repelRadius
            velocity.x += (dx / dist) * force * 0.016
            velocity.y += (dy / dist) * force * 0.016
          }
        }

        // integrate
        x += velocity.x
        y += velocity.y

        // walls
        if (x < width / 2) {
          x = width / 2
          velocity.x *= -bounce
        } else if (x > b.w - width / 2) {
          x = b.w - width / 2
          velocity.x *= -bounce
        }
        if (y < height / 2) {
          y = height / 2
          velocity.y *= -bounce
        } else if (y > b.h - height / 2) {
          y = b.h - height / 2
          velocity.y *= -bounce
        }

        // friction
        velocity.x *= friction
        velocity.y *= friction

        node.style.left = `${x}px`
        node.style.top = `${y}px`
        node.style.transform = 'translate(-50%, -50%)'
        node.dataset.x = `${x}`
        node.dataset.y = `${y}`
      })

      state.rafId = requestAnimationFrame(animate)
    }

    // start raf if requested earlier
    if (startRequested && state.rafId == null) {
      state.rafId = requestAnimationFrame(animate)
    }
    // raf starts when nodes are created

    return () => {
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('mousemove', onGlobalMove)
      window.removeEventListener('blur', onBlur)
      const ro = (overlayLayerRef.current as any)?.__ro
      if (ro && typeof ro.disconnect === 'function') {
        try { ro.disconnect() } catch {}
      }
    }
  }, [isDismantled, spreadContainerRef])

  const handleMouseEnter = () => {
    setIsHovered(true)
      setIsDismantled(true)
    restoringRef.current = false
  }

  const performRestore = (animateBack: boolean = false) => {
    if (!isDismantled && animationStateRef.current.nodes.length === 0) return
    // stop physics and move nodes back
    const state = animationStateRef.current
    if (state.rafId != null) {
      cancelAnimationFrame(state.rafId)
      state.rafId = null
    }
    const durationMs = animateBack ? 700 : 0
    const promises: Promise<void>[] = []
    state.nodes.forEach((node, idx) => {
      const origin = state.originals[idx]
      if (animateBack && origin) {
        node.style.transition = 'left 700ms ease, top 700ms ease, transform 700ms ease'
        node.style.left = `${origin.targetX}px`
        node.style.top = `${origin.targetY}px`
        node.style.transform = 'translate(-50%, -50%) scale(1)'
        promises.push(new Promise((resolve) => setTimeout(resolve, durationMs)))
      } else {
        promises.push(Promise.resolve())
      }
    })

    const finalize = () => {
      state.nodes.forEach((node, idx) => {
        try {
          const origin = state.originals[idx]
          const parent = origin?.parent as Node | null
          const sibling = origin?.nextSibling as ChildNode | null
          const placeholder = origin?.placeholder
          if (placeholder && placeholder.parentNode) {
            // swap placeholder back to node
            placeholder.parentNode.replaceChild(node, placeholder)
          } else if (parent && (parent as any).isConnected) {
            if (sibling && sibling.parentNode === parent) parent.insertBefore(node, sibling)
            else parent.appendChild(node)
          }
        } catch {}

        node.style.transition = ''
        node.style.position = 'relative'
        node.style.left = ''
        node.style.top = ''
        node.style.transform = ''
        node.style.pointerEvents = ''
        node.style.whiteSpace = ''
        try { delete (node as any).dataset.x } catch {}
        try { delete (node as any).dataset.y } catch {}
      })

      state.nodes = []
      state.velocities = []
      state.originals = []

      if (overlayLayerRef.current) {
        overlayLayerRef.current.remove()
        overlayLayerRef.current = null
      }

      setIsDismantled(false)
      restoringRef.current = false
    }

    Promise.all(promises).then(finalize)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    // leaving immediately starts the 5s outside timer; if user re-enters we'll cancel
    isPointerInsideRef.current = false
    if (outsideTimerRef.current != null) {
      clearTimeout(outsideTimerRef.current)
      outsideTimerRef.current = null
    }
    outsideTimerRef.current = window.setTimeout(() => {
      if (!isPointerInsideRef.current) {
        restoringRef.current = true
        performRestore(true)
      }
      if (outsideTimerRef.current != null) {
        clearTimeout(outsideTimerRef.current)
        outsideTimerRef.current = null
      }
    }, 5000)
  }

  return (
    <div
      ref={containerRef}
      className={`space-y-8 ${className}`}
    >
      {/* Title moved onto the border as a floating label */}

      <div ref={activeAreaRef} className="space-y-6 relative p-6 pt-10" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} onClick={(e) => e.stopPropagation()}>
        <div className={`absolute -top-3 left-4 px-2 py-0.5 text-sm font-bold font-mono ${isHovered ? 'text-red-400' : 'text-green-400'} bg-black/0`}>{'{ } TECH STACK'}</div>
        <div className="space-y-3">
          <h3 className={`text-sm font-semibold text-gray-400 tech-item transition-colors duration-300 ${isDismantled ? 'text-red-400' : ''}`}>
            Frontend Technologies:
          </h3>
          <div className="flex flex-wrap gap-2">
            {frontendTechs.map((tech, index) => (
              <span
                key={tech}
                ref={(el) => { techRefs.current[index] = el }}
                className={`tech-item px-3 py-1 text-xs font-mono bg-zinc-900 text-gray-300 rounded-md hover:bg-green-500 hover:text-black transition-all duration-300 cursor-pointer border border-zinc-800 ${isDismantled ? 'bg-red-900 text-red-300 border-red-600 shadow-lg shadow-red-500/20' : ''
                  }`}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <h3 className={`text-sm font-semibold text-gray-400 tech-item transition-colors duration-300 ${isDismantled ? 'text-red-400' : ''}`}>
            Backend & Web3 Development:
          </h3>
          <div className="flex flex-wrap gap-2">
            {backendTechs.map((tech, index) => (
              <span
                key={tech}
                ref={(el) => { techRefs.current[frontendTechs.length + index] = el }}
                className={`tech-item px-3 py-1 text-xs font-mono bg-zinc-900 text-gray-300 rounded-md hover:bg-green-500 hover:text-black transition-all duration-300 cursor-pointer border border-zinc-800 ${isDismantled ? 'bg-red-900 text-red-300 border-red-600 shadow-lg shadow-red-500/20' : ''
                  }`}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <h3 className={`text-sm font-semibold text-gray-400 tech-item transition-colors duration-300 ${isDismantled ? 'text-red-400' : ''}`}>
            Development Tools & Platforms:
          </h3>
          <div className="flex flex-wrap gap-2">
            {toolsTechs.map((tech, index) => (
              <span
                key={tech}
                ref={(el) => { techRefs.current[frontendTechs.length + backendTechs.length + index] = el }}
                className={`tech-item px-3 py-1 text-xs font-mono bg-zinc-900 text-gray-300 rounded-md hover:bg-green-500 hover:text-black transition-all duration-300 cursor-pointer border border-zinc-800 ${isDismantled ? 'bg-red-900 text-red-300 border-red-600 shadow-lg shadow-red-500/20' : ''
                  }`}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>

        {/* particles removed for cleaner look during dismantle */}
      </div>

      {/* Resume CTA placed BELOW the section */}
      <div className="mt-4">
        <a href="/resume" className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-green-500 text-black font-semibold hover:bg-green-400 transition-colors">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v12m0 0l-3-3m3 3l3-3M6 20h12"/></svg>
          <span>View Resume</span>
        </a>
      </div>
    </div>
  )
}