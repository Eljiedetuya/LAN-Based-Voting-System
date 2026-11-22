import React, {useEffect, useState} from 'react'

export function CandidatePhoto({src, name, size = 'regular', preview = false}) {
  const [failed, setFailed] = useState(false)
  useEffect(() => setFailed(false), [src])
  const initials = (name || '?').trim().split(/\s+/).slice(0, 2).map(part => part[0]).join('').toUpperCase()
  return src && !failed
    ? <img className={`candidate-avatar candidate-photo candidate-photo-${size}`} src={src} alt={`${name} profile`} onError={() => setFailed(true)} />
    : <div className={`candidate-avatar candidate-photo-fallback candidate-photo-${size}`} aria-label={`${name} profile placeholder`}>{initials}</div>
}

export function usePhotoPreview(file) {
  const [url, setUrl] = useState('')
  useEffect(() => {
    if (!file) { setUrl(''); return }
    const next = URL.createObjectURL(file)
    setUrl(next)
    return () => URL.revokeObjectURL(next)
  }, [file])
  return url
}
