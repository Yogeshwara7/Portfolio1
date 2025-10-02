"use client"

import { useEffect, useRef, useState } from "react"
import anime from "animejs"
import { Button } from "@/components/ui/button"
import AnimatedAvatar from "@/components/animated-avatar"
import InteractiveTechStack from "@/components/interactive-tech-stack"
// profile import removed; autofill comes from resume links provided

const GithubIcon = () => (
  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
  </svg>
)

const TwitterIcon = () => (
  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
)

const MailIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
    />
  </svg>
)

const LinkedinIcon = () => (
  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
  </svg>
)

export default function HeroSection() {
  const techStackRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)
  const ctaRef = useRef<HTMLDivElement>(null)
  const cursorRef = useRef<HTMLDivElement>(null)
  const heroGridRef = useRef<HTMLDivElement>(null)
  const [currentTime, setCurrentTime] = useState<string>("")
  const [currentDate, setCurrentDate] = useState<string>("")
  const titles = ["Full Stack Developer", "Web3 / DApp Developer"]
  const [titleIndex, setTitleIndex] = useState<number>(0)

  useEffect(() => {
    // Set current time and date on client side only
    const now = new Date()
    const dd = String(now.getDate()).padStart(2, '0')
    const mm = String(now.getMonth() + 1).padStart(2, '0')
    const yyyy = now.getFullYear()
    setCurrentDate(`${dd}/${mm}/${yyyy}`)
    setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))

    anime({
      targets: ".tech-item",
      translateX: [-50, 0],
      opacity: [0, 1],
      delay: anime.stagger(50, { start: 200 }),
      duration: 800,
      easing: "easeOutExpo",
    })

    anime({
      targets: ".profile-content",
      translateY: [30, 0],
      opacity: [0, 1],
      delay: anime.stagger(100, { start: 400 }),
      duration: 1000,
      easing: "easeOutExpo",
    })

    anime({
      targets: ".cta-card",
      scale: [0.9, 1],
      opacity: [0, 1],
      delay: 800,
      duration: 1000,
      easing: "easeOutElastic(1, .6)",
    })

    anime({
      targets: ".profile-image",
      translateY: [-10, 10],
      duration: 3000,
      loop: true,
      direction: "alternate",
      easing: "easeInOutSine",
    })

    const handleMouseMove = (e: MouseEvent) => {
      if (cursorRef.current) {
        anime({
          targets: cursorRef.current,
          left: e.clientX,
          top: e.clientY,
          duration: 1000,
          easing: "easeOutExpo",
        })
      }
    }

    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  useEffect(() => {
    const id = setInterval(() => {
      setTitleIndex((i) => (i + 1) % titles.length)
    }, 4500)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden bg-white dark:bg-black">
      <div ref={cursorRef} className="pointer-events-none fixed -translate-x-1/2 -translate-y-1/2 z-50 hidden lg:block">
        <div className="h-8 w-8 rounded-full border-2 border-green-500/30" />
      </div>

      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1a1a1a_1px,transparent_1px),linear-gradient(to_bottom,#1a1a1a_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30 [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_70%,transparent_110%)]" />

      <div ref={heroGridRef} className="relative z-10 grid grid-cols-1 lg:grid-cols-[280px_1fr_320px] gap-6 lg:gap-8 p-6 lg:p-8 max-w-7xl mx-auto min-h-screen">
        {/* Tech Stack - Hidden on mobile, shown on desktop in left column */}
        <div className="hidden lg:flex lg:items-center lg:justify-center">
          <InteractiveTechStack spreadContainerRef={heroGridRef as unknown as React.RefObject<HTMLDivElement>} />
        </div>

        <div ref={profileRef} className="flex flex-col items-center justify-center space-y-8 max-w-2xl mx-auto order-1 lg:order-none">
          <div className="profile-content relative">
            <div className="absolute inset-0 rounded-full bg-green-500/20 blur-2xl animate-pulse" />
            <AnimatedAvatar className="profile-image" />
          </div>

          <div className="profile-content text-center space-y-2">
            <h1 className="text-5xl font-bold text-black dark:text-white">Yogeshwara B</h1>
            <div className="flex items-center justify-center gap-2">
              <span className="text-xl text-gray-700 dark:text-gray-300">Hey,</span>
              <span className="text-xl">👋</span>
              <span className="text-xl text-gray-700 dark:text-gray-300">I&apos;m a</span>
              <span className="title-flip">
                <span className="text-xl font-semibold text-green-400 title-flip-item" key={titleIndex}>
                  {titles[titleIndex]}
                </span>
              </span>
            </div>
          </div>

          <div className="profile-content flex items-center gap-3 text-sm font-mono text-gray-600 dark:text-gray-400">
            {currentDate && <span>{currentDate}</span>}
            {currentDate && <span>•</span>}
            {currentTime && <span>{currentTime}</span>}
            {(currentDate || currentTime) && <span>•</span>}
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-green-400">Available for work</span>
            </div>
          </div>

          <p className="profile-content text-center text-gray-600 dark:text-gray-400 leading-relaxed max-w-xl">
            I craft fast, scalable, and user-friendly web applications with modern JavaScript frameworks - combining
            React on the frontend with robust server-side solutions using Node.js.
          </p>
        </div>

        {/* Tech Stack - Shown on mobile below profile */}
        <div className="lg:hidden order-2">
          <InteractiveTechStack spreadContainerRef={heroGridRef as unknown as React.RefObject<HTMLDivElement>} />
        </div>

        <div ref={ctaRef} className="flex flex-col justify-center space-y-6 order-3 lg:order-none">
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-black dark:text-white">LINKS.</h3>
            <div className="space-y-2">
              {[
                { icon: GithubIcon, label: "GitHub", href: "https://github.com/Yogeshwara7" },
                { icon: TwitterIcon, label: "X", href: "https://x.com/b_yogeshwara" },
                { icon: LinkedinIcon, label: "LinkedIn", href: "https://www.linkedin.com/in/yogeshwara7/" },
              ].map((link, i) => (
                <a
                  key={i}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center gap-3 p-3 bg-zinc-900 text-gray-300 rounded-lg hover:bg-green-500 hover:text-black transition-all group border border-zinc-800"
                >
                  <link.icon />
                  <span className="font-medium">{link.label}</span>
                </a>
              ))}
            </div>
          </div>

          <a href="/projects" className="block group">
            <div className="relative overflow-hidden rounded-2xl bg-black dark:bg-gradient-to-br dark:from-zinc-900 dark:via-zinc-900 dark:to-green-950/30 p-8 border border-zinc-800 hover:border-green-500/50 transition-all duration-300 cursor-pointer">
              <div className="hidden dark:block absolute inset-0 bg-gradient-to-br from-green-500/0 to-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative space-y-4 text-center">
                <div className="inline-block">
                  <div className="h-16 w-16 mx-auto rounded-full bg-zinc-800 dark:bg-green-500/10 flex items-center justify-center group-hover:bg-zinc-700 dark:group-hover:bg-green-500/20 transition-colors">
                    <svg className="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                      />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">VIEW</h3>
                  <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                    PROJECTS
                  </h3>
                </div>
                <p className="text-sm text-gray-400">Explore my latest work</p>
                <div className="flex items-center justify-center gap-2 text-green-500 group-hover:gap-4 transition-all">
                  <span className="text-sm font-mono">View All</span>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
              <div className="hidden dark:block absolute -bottom-10 -right-10 h-32 w-32 rounded-full bg-green-500/10 blur-3xl group-hover:bg-green-500/20 transition-colors" />
            </div>
          </a>

          <div className="cta-card relative overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-900 to-zinc-950 p-8 border border-zinc-800">
            <div className="absolute top-4 right-4">
              <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
            </div>
            <div className="space-y-6">
              <h2 className="text-3xl font-bold leading-tight text-balance text-white">
                READY TO TAKE YOUR IDEA TO THE NEXT LEVEL?
              </h2>
              <Button
                size="lg"
                className="w-full bg-green-500 text-black hover:bg-green-400 font-semibold text-lg py-6"
                onClick={() => window.open('mailto:yogeshwara567@gmail.com?subject=Project Inquiry&body=Hi Yogeshwara,%0D%0A%0D%0AI would like to discuss a project with you.%0D%0A%0D%0AProject Details:%0D%0A-%0D%0A-%0D%0A-%0D%0A%0D%0ABest regards', '_blank')}
              >
                Start Project
              </Button>
            </div>
            <div className="absolute -bottom-10 -right-10 h-32 w-32 rounded-full bg-green-500/10 blur-3xl" />
            <div className="absolute -top-10 -left-10 h-32 w-32 rounded-full bg-green-500/10 blur-3xl" />
          </div>
        </div>
      </div>
    </div>
  )
}
