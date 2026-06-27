import { useState, useRef } from 'react'
import { Upload, FileText, Plus, X, ChevronRight, Zap, Users, BarChart3 } from 'lucide-react'
import { rankCandidates } from '../lib/api'

function DropZone({ label, accept, multiple, onFiles, files, onRemove }) {
  const ref = useRef()
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files)
    onFiles(dropped)
  }

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => ref.current.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          dragging ? 'border-accent bg-accent/5' : 'border-border hover:border-muted'
        }`}
      >
        <Upload className="mx-auto mb-3 text-muted" size={28} />
        <p className="text-light font-medium">{label}</p>
        <p className="text-muted text-sm mt-1">PDF, DOCX, TXT · drag & drop or click</p>
        <input ref={ref} type="file" accept={accept} multiple={multiple} className="hidden"
          onChange={e => onFiles(Array.from(e.target.files))} />
      </div>
      {files && files.length > 0 && (
        <div className="space-y-2">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-3 bg-slate border border-border rounded-lg px-4 py-2.5">
              <FileText size={16} className="text-accent shrink-0" />
              <span className="text-light text-sm flex-1 truncate">{f.name}</span>
              <span className="text-muted text-xs">{(f.size / 1024).toFixed(0)}KB</span>
              <button onClick={(e) => { e.stopPropagation(); onRemove(i) }} className="text-muted hover:text-rose transition-colors">
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TextCandidateInput({ candidates, onChange }) {
  const addCandidate = () => onChange([...candidates, { name: '', text: '' }])
  const remove = (i) => onChange(candidates.filter((_, idx) => idx !== i))
  const update = (i, field, value) => {
    const next = [...candidates]
    next[i] = { ...next[i], [field]: value }
    onChange(next)
  }

  return (
    <div className="space-y-4">
      {candidates.map((c, i) => (
        <div key={i} className="bg-slate border border-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-ghost text-xs font-mono uppercase tracking-widest">Candidate {i + 1}</span>
            <button onClick={() => remove(i)} className="text-muted hover:text-rose transition-colors">
              <X size={14} />
            </button>
          </div>
          <input
            className="input-field text-sm"
            placeholder="Candidate name"
            value={c.name}
            onChange={e => update(i, 'name', e.target.value)}
          />
          <textarea
            className="input-field text-sm resize-none"
            rows={6}
            placeholder="Paste resume or profile text here..."
            value={c.text}
            onChange={e => update(i, 'text', e.target.value)}
          />
        </div>
      ))}
      <button onClick={addCandidate} className="btn-ghost w-full justify-center border border-dashed border-border">
        <Plus size={16} /> Add Candidate
      </button>
    </div>
  )
}

export default function UploadPage({ onResults }) {
  const [jdMode, setJdMode] = useState('text') // 'text' | 'file'
  const [jdText, setJdText] = useState('')
  const [jdFiles, setJdFiles] = useState([])
  const [candidateMode, setCandidateMode] = useState('files') // 'files' | 'text' | 'both'
  const [candidateFiles, setCandidateFiles] = useState([])
  const [textCandidates, setTextCandidates] = useState([{ name: '', text: '' }])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const canSubmit = (jdText.trim() || jdFiles.length > 0) &&
    (candidateFiles.length > 0 || textCandidates.some(c => c.text.trim()))

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const validTexts = textCandidates.filter(c => c.text.trim())
      const data = await rankCandidates({
        jdText: jdMode === 'text' ? jdText : undefined,
        jdFile: jdMode === 'file' ? jdFiles[0] : undefined,
        candidateFiles: candidateMode !== 'text' ? candidateFiles : [],
        candidateTexts: candidateMode !== 'files' ? validTexts : [],
      })
      onResults(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink">
      {/* Hero */}
      <div className="border-b border-border bg-slate/40">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="flex items-center gap-2 mb-6">
            <span className="badge bg-accent/10 text-accent">v1.0</span>
            <span className="text-muted text-sm">Hackathon Edition</span>
          </div>
          <h1 className="font-display text-5xl font-bold text-light leading-tight mb-4">
            TalentIQ
          </h1>
          <p className="text-ghost text-xl max-w-2xl">
            Hybrid candidate ranking — semantic understanding meets structured scoring. 
            Upload a job description and candidate profiles to get an AI-ranked shortlist with explanations.
          </p>
          <div className="flex gap-8 mt-8">
            {[
              { icon: Zap, label: 'Semantic + Skill Fit' },
              { icon: Users, label: 'Multi-signal Reranking' },
              { icon: BarChart3, label: 'Explainable Rankings' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 text-muted text-sm">
                <Icon size={15} className="text-accent" /> {label}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* JD */}
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-bold text-light">Job Description</h2>
            <div className="flex gap-1 bg-slate rounded-lg p-1 border border-border">
              {['text', 'file'].map(m => (
                <button key={m} onClick={() => setJdMode(m)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all capitalize ${
                    jdMode === m ? 'bg-accent text-white' : 'text-muted hover:text-light'
                  }`}>{m}</button>
              ))}
            </div>
          </div>

          {jdMode === 'text' ? (
            <textarea
              className="input-field resize-none"
              rows={16}
              placeholder="Paste your job description here — title, responsibilities, required skills, experience level..."
              value={jdText}
              onChange={e => setJdText(e.target.value)}
            />
          ) : (
            <DropZone
              label="Upload Job Description"
              accept=".pdf,.docx,.txt"
              multiple={false}
              onFiles={fs => setJdFiles(fs)}
              files={jdFiles}
              onRemove={() => setJdFiles([])}
            />
          )}
        </div>

        {/* Candidates */}
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-bold text-light">Candidates</h2>
            <div className="flex gap-1 bg-slate rounded-lg p-1 border border-border">
              {['files', 'text', 'both'].map(m => (
                <button key={m} onClick={() => setCandidateMode(m)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all capitalize ${
                    candidateMode === m ? 'bg-accent text-white' : 'text-muted hover:text-light'
                  }`}>{m}</button>
              ))}
            </div>
          </div>

          <div className="space-y-6 max-h-[520px] overflow-y-auto pr-1">
            {candidateMode !== 'text' && (
              <DropZone
                label="Upload Resumes / Profiles"
                accept=".pdf,.docx,.txt"
                multiple={true}
                onFiles={fs => setCandidateFiles(prev => [...prev, ...fs])}
                files={candidateFiles}
                onRemove={i => setCandidateFiles(candidateFiles.filter((_, idx) => idx !== i))}
              />
            )}
            {candidateMode !== 'files' && (
              <TextCandidateInput candidates={textCandidates} onChange={setTextCandidates} />
            )}
          </div>
        </div>
      </div>

      {/* Submit */}
      <div className="max-w-5xl mx-auto px-6 pb-16">
        {error && (
          <div className="bg-rose/10 border border-rose/30 text-rose rounded-lg px-4 py-3 mb-4 text-sm">
            {error}
          </div>
        )}
        <button onClick={handleSubmit} disabled={!canSubmit || loading} className="btn-primary text-base py-4 px-8">
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Ranking candidates...
            </>
          ) : (
            <>
              <Zap size={18} />
              Rank Candidates
              <ChevronRight size={16} />
            </>
          )}
        </button>
        {loading && (
          <p className="text-muted text-sm mt-3">
            Parsing documents, generating embeddings, and scoring candidates — this may take 20–60 seconds.
          </p>
        )}
      </div>
    </div>
  )
}
