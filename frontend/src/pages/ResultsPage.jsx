import { useState } from 'react'
import {
  Trophy, CheckCircle2, XCircle, ChevronDown, ChevronUp,
  Download, ArrowLeft, Clock, Users, Sparkles, TrendingUp,
  BarChart3, Target, Zap
} from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'
import { exportCSV } from '../lib/api'

const FIT_COLORS = {
  Strong: { bg: 'bg-emerald/10', text: 'text-emerald', border: 'border-emerald/30', dot: 'bg-emerald' },
  Good: { bg: 'bg-accent/10', text: 'text-accent', border: 'border-accent/30', dot: 'bg-accent' },
  Moderate: { bg: 'bg-amber/10', text: 'text-amber', border: 'border-amber/30', dot: 'bg-amber' },
  Weak: { bg: 'bg-rose/10', text: 'text-rose', border: 'border-rose/30', dot: 'bg-rose' },
}

const RANK_COLORS = ['text-amber', 'text-ghost', 'text-[#CD7F32]']

function ScoreCircle({ score, size = 'lg' }) {
  const r = size === 'lg' ? 36 : 24
  const stroke = size === 'lg' ? 4 : 3
  const circumference = 2 * Math.PI * r
  const offset = circumference - (score / 100) * circumference
  const dim = (r + stroke) * 2

  const color = score >= 80 ? '#10C27A' : score >= 65 ? '#5B6EF5' : score >= 45 ? '#F59E0B' : '#F43F5E'

  return (
    <div className={`relative ${size === 'lg' ? 'w-24 h-24' : 'w-14 h-14'} shrink-0`}>
      <svg viewBox={`0 0 ${dim} ${dim}`} className="w-full h-full -rotate-90">
        <circle cx={r + stroke} cy={r + stroke} r={r} fill="none" stroke="#2E3347" strokeWidth={stroke} />
        <circle cx={r + stroke} cy={r + stroke} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }} />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`font-display font-bold text-light ${size === 'lg' ? 'text-xl' : 'text-sm'}`}>
          {score.toFixed(0)}
        </span>
      </div>
    </div>
  )
}

function RadarCard({ breakdown }) {
  const data = [
    { subject: 'Semantic', value: breakdown.semantic_fit },
    { subject: 'Skills', value: breakdown.skill_match },
    { subject: 'Experience', value: breakdown.experience_relevance },
    { subject: 'Recency', value: breakdown.recency_progression },
  ]
  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <PolarGrid stroke="#2E3347" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#6B7394', fontSize: 11, fontFamily: 'Inter' }} />
          <Radar dataKey="value" stroke="#5B6EF5" fill="#5B6EF5" fillOpacity={0.15} strokeWidth={2} />
          <Tooltip
            contentStyle={{ background: '#22263A', border: '1px solid #2E3347', borderRadius: '8px', color: '#E8EAF2' }}
            formatter={(v) => [`${v.toFixed(1)}`, '']}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

function SkillPill({ skill, matched }) {
  return (
    <span className={`badge gap-1 ${
      matched
        ? 'bg-emerald/10 text-emerald border border-emerald/20'
        : 'bg-rose/10 text-rose border border-rose/20'
    }`}>
      {matched ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
      {skill}
    </span>
  )
}

function CandidateCard({ result, isTop3 }) {
  const [expanded, setExpanded] = useState(result.rank <= 3)
  const fit = FIT_COLORS[result.fit_band] || FIT_COLORS.Weak

  return (
    <div className={`card transition-all duration-200 ${
      result.rank === 1 ? 'border-amber/40 ring-1 ring-amber/20' : ''
    }`}>
      {/* Header */}
      <div className="flex items-start gap-4 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <ScoreCircle score={result.score} size={expanded ? 'lg' : 'sm'} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <span className={`font-mono text-sm font-bold ${RANK_COLORS[result.rank - 1] || 'text-muted'}`}>
              #{result.rank}
            </span>
            <h3 className="font-display text-lg font-bold text-light truncate">{result.name}</h3>
            <span className={`badge border ${fit.bg} ${fit.text} ${fit.border}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${fit.dot} mr-1`} />
              {result.fit_band}
            </span>
          </div>
          <p className="text-muted text-sm line-clamp-2">{result.explanation}</p>
        </div>
        <button className="text-muted hover:text-light shrink-0 mt-1">
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div className="mt-6 space-y-6 border-t border-border pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Radar */}
            <div>
              <h4 className="text-ghost text-xs font-mono uppercase tracking-widest mb-3">Score Breakdown</h4>
              <RadarCard breakdown={result.score_breakdown} />
              <div className="grid grid-cols-2 gap-2 mt-2">
                {[
                  { label: 'Semantic', val: result.score_breakdown.semantic_fit },
                  { label: 'Skills', val: result.score_breakdown.skill_match },
                  { label: 'Experience', val: result.score_breakdown.experience_relevance },
                  { label: 'Recency', val: result.score_breakdown.recency_progression },
                ].map(({ label, val }) => (
                  <div key={label} className="bg-slate rounded-lg px-3 py-2">
                    <div className="text-muted text-xs mb-1">{label}</div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-border rounded-full h-1.5">
                        <div className="bg-accent h-1.5 rounded-full" style={{ width: `${val}%` }} />
                      </div>
                      <span className="text-ghost text-xs font-mono w-8 text-right">{val.toFixed(0)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skills + Highlights */}
            <div className="space-y-4">
              {result.highlights.length > 0 && (
                <div>
                  <h4 className="text-ghost text-xs font-mono uppercase tracking-widest mb-2">Key Highlights</h4>
                  <ul className="space-y-1.5">
                    {result.highlights.map((h, i) => (
                      <li key={i} className="flex gap-2 text-sm text-ghost">
                        <Sparkles size={13} className="text-accent mt-0.5 shrink-0" />
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.matched_skills.length > 0 && (
                <div>
                  <h4 className="text-ghost text-xs font-mono uppercase tracking-widest mb-2">Matched Skills</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {result.matched_skills.map(s => <SkillPill key={s} skill={s} matched />)}
                  </div>
                </div>
              )}

              {result.missing_skills.length > 0 && (
                <div>
                  <h4 className="text-ghost text-xs font-mono uppercase tracking-widest mb-2">Missing Must-Haves</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {result.missing_skills.map(s => <SkillPill key={s} skill={s} matched={false} />)}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function JobSummary({ job }) {
  return (
    <div className="card mb-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="text-ghost text-xs font-mono uppercase tracking-widest mb-1">Ranked For</p>
          <h2 className="font-display text-2xl font-bold text-light">{job.title || 'Unknown Role'}</h2>
          {job.domain && <p className="text-muted mt-1">{job.domain} · {job.seniority}</p>}
        </div>
        <div className="flex gap-6">
          <div>
            <p className="text-muted text-xs mb-0.5">Must-Have Skills</p>
            <p className="text-light font-bold text-lg">{job.must_have_skills?.length || 0}</p>
          </div>
          <div>
            <p className="text-muted text-xs mb-0.5">Min. Experience</p>
            <p className="text-light font-bold text-lg">{job.min_years_experience || 0}y</p>
          </div>
        </div>
      </div>
      {job.must_have_skills?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {job.must_have_skills.map(s => (
            <span key={s} className="badge bg-accent/10 text-accent border border-accent/20">{s}</span>
          ))}
          {job.preferred_skills?.slice(0, 5).map(s => (
            <span key={s} className="badge bg-panel text-muted border border-border">{s}</span>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ResultsPage({ data, onReset }) {
  const { job_parsed, shortlist, total_candidates, processing_time_seconds } = data

  const handleExport = async () => {
    try {
      await exportCSV(shortlist)
    } catch (e) {
      console.error('Export failed', e)
    }
  }

  return (
    <div className="min-h-screen bg-ink">
      {/* Top bar */}
      <div className="border-b border-border bg-slate/40 sticky top-0 z-10 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={onReset} className="btn-ghost text-sm">
              <ArrowLeft size={15} /> New Search
            </button>
            <div className="h-5 w-px bg-border" />
            <h1 className="font-display font-bold text-light text-lg">TalentIQ</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-muted text-sm">
              <Clock size={13} />
              {processing_time_seconds}s
              <span className="text-border">·</span>
              <Users size={13} />
              {total_candidates} candidates
            </div>
            <button onClick={handleExport} className="btn-primary text-sm py-2">
              <Download size={14} /> Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="border-b border-border bg-slate/20">
        <div className="max-w-5xl mx-auto px-6 py-4 flex gap-8">
          {[
            { label: 'Shortlisted', val: shortlist.length, icon: Target },
            { label: 'Strong Fit', val: shortlist.filter(r => r.fit_band === 'Strong').length, icon: TrendingUp },
            { label: 'Good Fit', val: shortlist.filter(r => r.fit_band === 'Good').length, icon: BarChart3 },
            { label: 'Top Score', val: `${shortlist[0]?.score.toFixed(0) || 0}`, icon: Zap },
          ].map(({ label, val, icon: Icon }) => (
            <div key={label} className="flex items-center gap-3">
              <Icon size={15} className="text-accent" />
              <span className="text-light font-bold text-lg font-display">{val}</span>
              <span className="text-muted text-sm">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        <JobSummary job={job_parsed} />

        <h2 className="font-display text-xl font-bold text-light mb-4">
          Ranked Shortlist
        </h2>

        <div className="space-y-4">
          {shortlist.map(result => (
            <CandidateCard key={result.id} result={result} isTop3={result.rank <= 3} />
          ))}
        </div>

        {shortlist.length === 0 && (
          <div className="text-center py-16 text-muted">
            No candidates ranked. Try adjusting your JD or candidate inputs.
          </div>
        )}
      </div>
    </div>
  )
}
