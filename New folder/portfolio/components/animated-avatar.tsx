"use client"

import { useEffect, useRef, useState } from "react"
import { useTheme } from "@/components/theme-provider"

interface AnimatedAvatarProps {
    className?: string
}

export default function AnimatedAvatar({ className = "" }: AnimatedAvatarProps) {
    const { theme, toggleTheme } = useTheme()
    const avatarRef = useRef<HTMLDivElement>(null)
    const leftEyeRef = useRef<HTMLDivElement>(null)
    const rightEyeRef = useRef<HTMLDivElement>(null)
    const faceRef = useRef<HTMLDivElement>(null)
    const ringRef = useRef<HTMLDivElement>(null)
    const mouthRef = useRef<HTMLDivElement>(null)
    const leftLidRef = useRef<HTMLDivElement>(null)
    const rightLidRef = useRef<HTMLDivElement>(null)
    const [isBlinking, setIsBlinking] = useState(false)
    const [isHover, setIsHover] = useState(false)
    const [isSurprised, setIsSurprised] = useState(false)
    const [isSleeping, setIsSleeping] = useState(false)
    const lastActivityRef = useRef<number>(performance.now())

    useEffect(() => {
        let rafId: number | null = null
        let lastX = 0
        let lastY = 0
        let lastT = performance.now()
        let idleTimer: number | null = null
        let saccadeTimer: number | null = null

        const handleMouseMove = (e: MouseEvent) => {
            if (!avatarRef.current || !leftEyeRef.current || !rightEyeRef.current) return

            const avatarRect = avatarRef.current.getBoundingClientRect()
            const cx = avatarRect.left + avatarRect.width / 2
            const cy = avatarRect.top + avatarRect.height / 2

            const dx = e.clientX - cx
            const dy = e.clientY - cy
            const angle = Math.atan2(dy, dx)
            const dist = Math.min(Math.hypot(dx, dy) / 10, 8)
            const eyeX = Math.cos(angle) * dist
            const eyeY = Math.sin(angle) * dist

            // face tilt & bob towards the cursor
            const tiltX = Math.max(-8, Math.min(8, -dy / 40))
            const tiltY = Math.max(-8, Math.min(8, dx / 40))

            // compute speed (px/ms)
            const now = performance.now()
            const dt = Math.max(1, now - lastT)
            const vx = (e.clientX - lastX) / dt
            const vy = (e.clientY - lastY) / dt
            const speed = Math.min(0.02, Math.hypot(vx, vy))
            lastX = e.clientX
            lastY = e.clientY
            lastT = now

            lastActivityRef.current = performance.now()
            if (isSleeping) setIsSleeping(false)

            rafId = requestAnimationFrame(() => {
                leftEyeRef.current!.style.transform = `translate(${eyeX}px, ${eyeY}px)`
                rightEyeRef.current!.style.transform = `translate(${eyeX}px, ${eyeY}px)`
                const scale = 1 + speed * 20 // 1..1.4
                leftEyeRef.current!.style.scale = `${scale}`
                rightEyeRef.current!.style.scale = `${scale}`
                if (faceRef.current) {
                    faceRef.current.style.transform = `rotateX(${tiltX}deg) rotateY(${tiltY}deg)`
                }
                if (ringRef.current) {
                    ringRef.current.style.transform = `rotateX(${tiltX * 1.2}deg) rotateY(${tiltY * 1.2}deg) translateZ(0)`
                }
                if (mouthRef.current) {
                    // mouth smiles more when cursor is near
                    const smile = Math.max(0, 18 - Math.min(18, Math.hypot(dx, dy) / 10))
                    mouthRef.current.style.borderTopLeftRadius = `${smile}px`
                    mouthRef.current.style.borderTopRightRadius = `${smile}px`
                    mouthRef.current.style.height = `${8 + smile / 2}px`
                }
            })

            // surprise on fast flicks
            if (speed > 0.015 && !isSurprised) {
                setIsSurprised(true)
                window.setTimeout(() => setIsSurprised(false), 320)
            }

            // reset idle saccade timers
            if (idleTimer) { clearTimeout(idleTimer) }
            if (saccadeTimer) { clearTimeout(saccadeTimer) }
            idleTimer = window.setTimeout(() => {
                // small random saccades while idle
                const doSaccade = () => {
                    const sx = (Math.random() - 0.5) * 6
                    const sy = (Math.random() - 0.5) * 6
                    leftEyeRef.current!.style.transform = `translate(${sx}px, ${sy}px)`
                    rightEyeRef.current!.style.transform = `translate(${sx}px, ${sy}px)`
                    saccadeTimer = window.setTimeout(doSaccade, 1200 + Math.random() * 1200)
                }
                doSaccade()
            }, 2000)
        }

        window.addEventListener("mousemove", handleMouseMove)

        // gentle floating animation
        let t = 0
        const float = () => {
            t += 0.016
            if (avatarRef.current) {
                const y = Math.sin(t) * 4
                avatarRef.current.style.transform = `translateY(${y}px)`
            }
            rafId = requestAnimationFrame(float)
        }
        rafId = requestAnimationFrame(float)

        return () => {
            window.removeEventListener("mousemove", handleMouseMove)
            if (rafId) cancelAnimationFrame(rafId)
            if (idleTimer) clearTimeout(idleTimer)
            if (saccadeTimer) clearTimeout(saccadeTimer)
        }
    }, [])

    // blinking lids
    useEffect(() => {
        let timeoutId: number | null = null
        const blink = () => {
            setIsBlinking(true)
            timeoutId = window.setTimeout(() => setIsBlinking(false), 120)
            const next = 2000 + Math.random() * 4000
            timeoutId = window.setTimeout(blink, next)
        }
        timeoutId = window.setTimeout(blink, 1800)
        return () => {
            if (timeoutId) clearTimeout(timeoutId)
        }
    }, [])

    // sleep mode after 30s inactivity (and not hovered)
    useEffect(() => {
        const check = () => {
            const idleMs = performance.now() - lastActivityRef.current
            if (!isHover && idleMs > 30000) {
                setIsSleeping(true)
            } else if (isSleeping && (isHover || idleMs <= 30000)) {
                setIsSleeping(false)
            }
        }
        const id = window.setInterval(check, 1000)
        return () => clearInterval(id)
    }, [isHover, isSleeping])

    // wink on click and toggle theme
    const handleClick = () => {
        // Wink animation
        if (leftLidRef.current) {
            leftLidRef.current.style.transition = 'transform 120ms'
            leftLidRef.current.style.transform = 'translateY(0)'
            window.setTimeout(() => {
                leftLidRef.current && (leftLidRef.current.style.transform = 'translateY(-100%)')
            }, 160)
        }
        // Toggle theme
        toggleTheme()
    }

    return (
        <div ref={avatarRef} className={`relative ${className}`} onMouseEnter={() => { setIsHover(true); lastActivityRef.current = performance.now(); if (isSleeping) setIsSleeping(false) }} onMouseLeave={() => setIsHover(false)} onClick={handleClick}>
            {/* Face */}
            <div className="relative" style={{ perspective: 800 }}>
                <div ref={ringRef} className={`absolute -inset-2 rounded-full border-4 ${isHover ? 'border-green-400' : 'border-green-500'} shadow-[0_0_60px_rgba(34,197,94,0.45)] transition-transform duration-150 pointer-events-none`}></div>
                <div ref={faceRef} className={`relative w-64 h-64 rounded-full border-4 ${isHover ? 'border-green-400' : 'border-green-500'} shadow-[0_0_50px_rgba(34,197,94,0.5)] ${theme === 'dark' ? 'bg-gradient-to-br from-zinc-900 to-black' : 'bg-gradient-to-br from-gray-100 to-white'} flex items-center justify-center transition-transform duration-150 will-change-transform [transform-style:preserve-3d]`}>

                {/* Left Eye */}
                <div className={`absolute left-16 w-12 h-12 ${theme === 'dark' ? 'bg-white' : 'bg-gray-800'} rounded-full flex items-center justify-center overflow-hidden`}>
                    <div ref={leftLidRef} className={`absolute inset-0 ${theme === 'dark' ? 'bg-zinc-900/95' : 'bg-gray-100/95'} transition-all duration-150 ${isBlinking || isSleeping ? 'translate-y-0' : '-translate-y-full'}`}></div>
                    <div
                        ref={leftEyeRef}
                        className={`w-6 h-6 ${theme === 'dark' ? 'bg-black' : 'bg-white'} rounded-full transition-transform duration-100 ease-out`}
                    ></div>
                </div>

                {/* Right Eye */}
                <div className={`absolute right-16 w-12 h-12 ${theme === 'dark' ? 'bg-white' : 'bg-gray-800'} rounded-full flex items-center justify-center overflow-hidden`}>
                    <div ref={rightLidRef} className={`absolute inset-0 ${theme === 'dark' ? 'bg-zinc-900/95' : 'bg-gray-100/95'} transition-all duration-150 ${isBlinking || isSleeping ? 'translate-y-0' : '-translate-y-full'}`}></div>
                    <div
                        ref={rightEyeRef}
                        className={`w-6 h-6 ${theme === 'dark' ? 'bg-black' : 'bg-white'} rounded-full transition-transform duration-100 ease-out`}
                    ></div>
                </div>

                {/* Mouth */}
                <div ref={mouthRef} className={`absolute bottom-14 ${isSleeping ? 'w-10 h-1 rounded-full' : isSurprised ? 'w-6 h-6 rounded-full' : 'w-16 h-2 rounded-b-full'} ${theme === 'dark' ? 'bg-white/90' : 'bg-gray-800/90'} transition-all duration-200`}></div>

                {/* Animated glow effect */}
                <div className="absolute inset-0 rounded-full bg-green-500/10 animate-pulse"></div>
                <div className="pointer-events-none absolute -inset-2 rounded-full shadow-[0_0_80px_rgba(34,197,94,0.35)]"></div>
                {/* Sleep Zzz */}
                {isSleeping && (
                    <div className="absolute -top-2 -right-2 text-green-400/80 select-none">
                        <div className="animate-pulse">z</div>
                        <div className="mt-1 animate-pulse">z</div>
                        <div className="mt-1 animate-pulse">z</div>
                    </div>
                )}
                </div>
            </div>
        </div>
    )
}
