"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import anime from "animejs"
import Link from "next/link"
import { Atom, Server, Database, Wallet, Layers, Boxes, Coins, ChartBar, GitBranch, Globe, AppWindow, Cpu } from "lucide-react"
import { useTheme } from "@/components/theme-provider"

type Repo = {
  id: number
  name: string
  description: string | null
  html_url: string
  stargazers_count: number
  language: string | null
  topics?: string[]
  created_at: string
  updated_at: string
}

const manualFeatured = [
  {
    key: "Washitec",
    title: "Washitec — Laundry Service Management Platform",
    description:
      "Full laundry service management with user app + admin panel: bookings, plans, payments (Razorpay), real-time notifications (FCM), analytics, college-specific pricing, role-based access, and secure backend APIs.",
    image: "/placeholder.svg",
    stack: [
      "React 18",
      "TypeScript",
      "Node.js",
      "Express.js",
      "Firebase",
      "Razorpay",
      "Vercel",
      "Render",
    ],
    category: "Full-Stack",
    year: new Date().getFullYear().toString(),
    href: "#", // private repo placeholder
  },
]

export default function ProjectsPage() {
  const { theme } = useTheme()
  const headerRef = useRef<HTMLDivElement>(null)
  const projectsRef = useRef<HTMLDivElement>(null)
  const [repos, setRepos] = useState<Repo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<number>(0)
  const [showProgress, setShowProgress] = useState<boolean>(true)

  const IconFor = ({ language, name, size = 96 }: { language?: string | null; name?: string; size?: number }) => {
    const n = (name || '').toLowerCase()
    const lang = (language || '').toLowerCase()
    const common = (keys: string[]) => keys.some(k => n.includes(k))
    let Icon = Boxes
    if (lang.includes('javascript') || n.includes('react') || n.includes('next')) Icon = Atom
    else if (lang.includes('typescript')) Icon = Atom
    else if (lang.includes('python')) Icon = Database
    else if (lang.includes('java')) Icon = Cpu
    else if (lang.includes('solidity') || common(['web3', 'wallet', 'eth', 'ethereum', 'crypto'])) Icon = Coins
    else if (lang.includes('go')) Icon = Server
    else if (lang.includes('ruby')) Icon = Server
    else if (lang.includes('node') || common(['server', 'api'])) Icon = Server
    else if (lang.includes('sql') || lang.includes('postgres') || common(['db', 'data'])) Icon = Database
    else if (common(['dashboard', 'analytics', 'chart'])) Icon = ChartBar
    else if (common(['fundraiser', 'donate'])) Icon = Wallet
    else if (common(['site', 'web', 'app'])) Icon = AppWindow
    else if (common(['global', 'globe'])) Icon = Globe
    else if (common(['core', 'engine', 'lib'])) Icon = Layers
    else if (common(['git'])) Icon = GitBranch
    return <Icon className="text-green-400" size={size} />
  }

  useEffect(() => {
    // Animate header
    anime({
      targets: ".page-header",
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 1000,
      easing: "easeOutExpo",
    })

    // Animate project cards with stagger
    anime({
      targets: ".project-card",
      translateY: [60, 0],
      opacity: [0, 1],
      delay: anime.stagger(100, { start: 300 }),
      duration: 1000,
      easing: "easeOutExpo",
    })

    // Animate tech stack badges
    anime({
      targets: ".tech-badge",
      scale: [0, 1],
      delay: anime.stagger(30, { start: 800 }),
      duration: 600,
      easing: "easeOutElastic(1, .6)",
    })
  }, [])

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        setShowProgress(true)
        setProgress(0)
        // fake progressive loading to 90%
        let p = 0
        const timer = setInterval(() => {
          p = Math.min(90, p + Math.max(1, Math.floor(Math.random() * 7)))
          setProgress(p)
        }, 120)
        const url = "https://api.github.com/users/Yogeshwara7/repos?per_page=100"
        const fetchOnce = () => fetch(url, { headers: { 'Accept': 'application/vnd.github+json' } })
        let res = await fetchOnce()
        if (!res.ok) {
          await new Promise(r => setTimeout(r, 800))
          res = await fetchOnce()
        }
        if (!res.ok) throw new Error(`GitHub API error: ${res.status}`)
        const data: Repo[] = await res.json()
        const excluded = new Set(["yogeshwara7", "java_assignment", "java-assignment"]) as Set<string>
        const filtered = data.filter(r => !excluded.has(r.name.toLowerCase()))
        filtered.sort((a, b) => (b.stargazers_count - a.stargazers_count) || (new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()))
        setRepos(filtered)
        // complete progress
        setProgress(100)
        clearInterval(timer)
        setTimeout(() => setShowProgress(false), 400)
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load repositories")
        setProgress(0)
        setShowProgress(false)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const timeline = useMemo(() => {
    const list = repos.filter(r => r.name.toLowerCase() !== 'fundraiser').slice().sort((a,b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    return list
  }, [repos])

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'}`}>
      {/* Background grid */}
      <div className={`fixed inset-0 ${theme === 'dark' ? 'bg-[linear-gradient(to_right,#1a1a1a_1px,transparent_1px),linear-gradient(to_bottom,#1a1a1a_1px,transparent_1px)]' : 'bg-[linear-gradient(to_right,#e5e5e5_1px,transparent_1px),linear-gradient(to_bottom,#e5e5e5_1px,transparent_1px)]'} bg-[size:4rem_4rem] opacity-20`} />

      {/* Gradient orbs */}
      <div className="fixed top-0 left-1/4 h-96 w-96 rounded-full bg-green-500/10 blur-3xl" />
      <div className="fixed bottom-0 right-1/4 h-96 w-96 rounded-full bg-green-500/10 blur-3xl" />

      <div className="relative z-10">
        {/* Header */}
        <div
          ref={headerRef}
          className={`page-header ${theme === 'dark' ? 'border-b border-zinc-800 bg-black/50' : 'border-b border-gray-300 bg-white/50'} backdrop-blur-sm sticky top-0 z-50`}
        >
          <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
            <Link
              href="/"
              className={`flex items-center gap-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} hover:text-green-400 transition-colors group`}
            >
              <svg
                className="h-5 w-5 group-hover:-translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-mono text-sm">Back</span>
            </Link>

            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold font-mono">
                <span className="text-green-400">{"<"}</span>
                PROJECTS
                <span className="text-green-400">{"/>"}</span>
              </h1>
              <p className={`${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} text-sm mt-2 font-mono`}>Showcasing innovation through code</p>
            </div>

            <div className="w-20" />
          </div>
          {showProgress && (
            <div className="relative">
              <div className={`h-1 w-full ${theme === 'dark' ? 'bg-zinc-900/60' : 'bg-gray-200'}`}>
                <div
                  className="h-1 bg-green-500 transition-[width] duration-150"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="absolute -top-5 right-4 text-xs font-mono text-green-400">{Math.max(0, Math.min(100, Math.floor(progress)))}%</div>
            </div>
          )}
        </div>

        {/* Projects Grid */}
        <div ref={projectsRef} className="max-w-7xl mx-auto px-6 py-16">
          {!loading && !error && (
          <div className="mb-20">
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-12 bg-green-500" />
              <h2 className="text-2xl font-bold text-green-400 font-mono">FEATURED</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Private/Manual featured first */}
              {manualFeatured.map((p) => (
                <div
                  key={p.key}
                  className={`project-card group relative overflow-hidden rounded-2xl ${theme === 'dark' ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-gray-300 shadow-lg'} border hover:border-green-500/50 transition-all duration-500`}
                >
                  <div className={`relative h-64 overflow-hidden flex items-center justify-center ${theme === 'dark' ? 'bg-gradient-to-br from-zinc-900 via-zinc-900 to-green-950/20' : 'bg-gradient-to-br from-gray-200 via-gray-100 to-green-50/30'}`}>
                    <IconFor name={p.title} language={p.category} />
                    <div className={`absolute inset-0 ${theme === 'dark' ? 'bg-gradient-to-t from-zinc-900/30 to-transparent' : 'bg-gradient-to-t from-white/40 to-transparent'}`} />
                    <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-black text-xs font-bold rounded-full">
                      {p.category}
                    </div>
                  </div>
                  <div className="p-6 space-y-4">
                    <div className="flex items-start justify-between">
                      <h3 className={`text-2xl font-bold group-hover:text-green-400 transition-colors break-all ${theme === 'dark' ? 'text-white' : 'text-black'}`}>{p.title}</h3>
                      <span className={`text-xs font-mono ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>{p.year}</span>
                    </div>
                    <p className={`leading-relaxed text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{p.description}</p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {p.stack.map((tech, i) => (
                        <span key={i} className={`tech-badge px-3 py-1 text-xs font-mono ${theme === 'dark' ? 'bg-black' : 'bg-white'} text-green-400 rounded-md border border-green-500/30`}>
                          {tech}
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-3 pt-4">
                      <span className={`flex-1 px-4 py-2 ${theme === 'dark' ? 'bg-zinc-800 text-gray-300' : 'bg-gray-200 text-gray-700'} font-semibold rounded-lg text-center`}>Private Repository</span>
                    </div>
                  </div>
                  <div className="absolute inset-0 border-2 border-green-500/0 group-hover:border-green-500/20 rounded-2xl transition-colors pointer-events-none" />
                </div>
              ))}

              {(() => {
                const fundraiser = repos.find(r => r.name.toLowerCase() === 'fundraiser')
                return fundraiser ? [fundraiser] : []
              })().map((repo) => (
                  <div
                    key={repo.id}
                    className={`project-card group relative overflow-hidden rounded-2xl ${theme === 'dark' ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-gray-300 shadow-lg'} border hover:border-green-500/50 transition-all duration-500`}
                  >
                    {/* Project Image */}
                    <div className={`relative h-64 overflow-hidden flex items-center justify-center ${theme === 'dark' ? 'bg-gradient-to-br from-zinc-900 via-zinc-900 to-green-950/20' : 'bg-gradient-to-br from-gray-200 via-gray-100 to-green-50/30'}`}>
                      <IconFor name={repo.name} language={repo.language} />
                      <div className={`absolute inset-0 ${theme === 'dark' ? 'bg-gradient-to-t from-zinc-900/30 to-transparent' : 'bg-gradient-to-t from-white/40 to-transparent'}`} />

                      {/* Category badge */}
                      <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-black text-xs font-bold rounded-full">
                        {repo.language || "Repo"}
                      </div>
                    </div>

                    {/* Project Info */}
                    <div className="p-6 space-y-4">
                      <div className="flex items-start justify-between">
                        <h3 className={`text-2xl font-bold group-hover:text-green-400 transition-colors break-all ${theme === 'dark' ? 'text-white' : 'text-black'}`}>
                          {repo.name}
                        </h3>
                        <span className={`text-xs font-mono ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>{new Date(repo.created_at).getFullYear()}</span>
                      </div>

                      <p className={`leading-relaxed text-sm min-h-12 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{repo.description || "No description provided."}</p>

                      {/* Tech Stack */}
                      <div className="flex flex-wrap gap-2 pt-2">
                        {[repo.language].filter(Boolean).map((tech, i) => (
                          <span
                            key={i}
                            className={`tech-badge px-3 py-1 text-xs font-mono ${theme === 'dark' ? 'bg-black' : 'bg-gray-800'} text-green-400 rounded-md border border-green-500/30`}
                          >
                            {tech}
                          </span>
                        ))}
                      </div>

                      {/* Action buttons */}
                      <div className="flex gap-3 pt-4">
                        <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="flex-1 text-center px-4 py-2 bg-green-500 text-black font-semibold rounded-lg hover:bg-green-400 transition-colors">
                          Open on GitHub
                        </a>
                        <button className={`px-4 py-2 border ${theme === 'dark' ? 'border-zinc-700' : 'border-gray-300'} rounded-lg hover:border-green-500 hover:text-green-400 transition-colors`}>
                          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    {/* Hover effect overlay */}
                    <div className="absolute inset-0 border-2 border-green-500/0 group-hover:border-green-500/20 rounded-2xl transition-colors pointer-events-none" />
                  </div>
                ))}
            </div>
          </div>
          )}

          {/* All Projects — Center Trunk Timeline */}
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-12 bg-green-500" />
              <h2 className="text-2xl font-bold text-green-400 font-mono">ALL PROJECTS</h2>
            </div>

            {/* Loading / Error */}
            {loading && (
              <div className="space-y-6">
                {[1,2,3,4].map(i => (
                  <div key={i} className={`h-28 ${theme === 'dark' ? 'bg-zinc-900/60 border-zinc-800' : 'bg-gray-200 border-gray-300'} rounded-lg border animate-pulse`} />
                ))}
              </div>
            )}
            {error && (
              <div className="p-4 bg-red-950/40 border border-red-800 rounded text-red-300 flex items-center justify-between">
                <span>Network error loading projects. GitHub may be rate-limiting. Please retry.</span>
                <button onClick={() => { setError(null); setRepos([]); setLoading(true); setShowProgress(true); setProgress(0); window.location.reload() }} className="px-3 py-1 bg-red-600/20 border border-red-600/40 rounded hover:bg-red-600/30">Retry</button>
              </div>
            )}

            {!loading && !error && (
              <div className="relative">
                {/* Center trunk */}
                <div className={`absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-px ${theme === 'dark' ? 'bg-zinc-800' : 'bg-gray-300'}`} />
                <div className="space-y-10">
                  {timeline.map((repo, idx) => {
                    const sideLeft = idx % 2 === 0
                    return (
                      <div key={repo.id} className={`grid grid-cols-[1fr_2px_1fr] items-stretch gap-6`}>
                        {/* Left branch */}
                        <div className={`relative ${sideLeft ? '' : 'hidden md:block'}`}>
                          {sideLeft && (
                            <div className="ml-auto max-w-xl">
                              <div className={`relative project-card overflow-hidden rounded-xl ${theme === 'dark' ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-gray-300 shadow-md'} border hover:border-green-500/50 transition-all duration-500 hover:-translate-y-1`}>
                                <div className={`absolute right-0 top-1/2 -translate-y-1/2 h-px w-8 ${theme === 'dark' ? 'bg-zinc-700' : 'bg-gray-400'}`} />
                                <div className="p-5 space-y-3">
                                  <div className="flex items-center justify-between">
                                    <h3 className={`text-lg font-bold group-hover:text-green-400 transition-colors break-all ${theme === 'dark' ? 'text-white' : 'text-black'}`}>{repo.name}</h3>
                                    <span className={`text-xs font-mono ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>{new Date(repo.created_at).getFullYear()}</span>
                                  </div>
                                  <div className="flex items-center gap-3">
                                    <IconFor name={repo.name} language={repo.language} size={40} />
                                    <p className={`text-sm line-clamp-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{repo.description || 'No description provided.'}</p>
                                  </div>
                                  <div className="flex flex-wrap gap-1.5">
                                    {[repo.language].filter(Boolean).map((tech, i) => (
                                      <span key={i} className={`px-2 py-0.5 text-xs font-mono ${theme === 'dark' ? 'bg-black' : 'bg-gray-800'} text-green-400 rounded border border-green-500/30`}>{tech}</span>
                                    ))}
                                  </div>
                                  <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className={`inline-block mt-1 px-3 py-1.5 ${theme === 'dark' ? 'bg-zinc-800 text-gray-300' : 'bg-gray-200 text-gray-700'} font-semibold rounded hover:bg-green-500 hover:text-black transition-colors text-xs`}>Open on GitHub</a>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                        {/* Center line gap */}
                        <div />
                        {/* Right branch */}
                        <div className={`relative ${!sideLeft ? '' : 'hidden md:block'}`}>
                          {!sideLeft && (
                            <div className="max-w-xl">
                              <div className={`relative project-card overflow-hidden rounded-xl ${theme === 'dark' ? 'bg-zinc-900 border-zinc-800' : 'bg-white border-gray-300 shadow-md'} border hover:border-green-500/50 transition-all duration-500 hover:-translate-y-1`}>
                                <div className={`absolute left-0 top-1/2 -translate-y-1/2 h-px w-8 ${theme === 'dark' ? 'bg-zinc-700' : 'bg-gray-400'}`} />
                                <div className="p-5 space-y-3">
                                  <div className="flex items-center justify-between">
                                    <h3 className={`text-lg font-bold group-hover:text-green-400 transition-colors break-all ${theme === 'dark' ? 'text-white' : 'text-black'}`}>{repo.name}</h3>
                                    <span className={`text-xs font-mono ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>{new Date(repo.created_at).getFullYear()}</span>
                                  </div>
                                  <div className="flex items-center gap-3">
                                    <IconFor name={repo.name} language={repo.language} size={40} />
                                    <p className={`text-sm line-clamp-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{repo.description || 'No description provided.'}</p>
                                  </div>
                                  <div className="flex flex-wrap gap-1.5">
                                    {[repo.language].filter(Boolean).map((tech, i) => (
                                      <span key={i} className={`px-2 py-0.5 text-xs font-mono ${theme === 'dark' ? 'bg-black' : 'bg-gray-800'} text-green-400 rounded border border-green-500/30`}>{tech}</span>
                                    ))}
                                  </div>
                                  <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className={`inline-block mt-1 px-3 py-1.5 ${theme === 'dark' ? 'bg-zinc-800 text-gray-300' : 'bg-gray-200 text-gray-700'} font-semibold rounded hover:bg-green-500 hover:text-black transition-colors text-xs`}>Open on GitHub</a>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
