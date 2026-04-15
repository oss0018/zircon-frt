import { useCallback, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useTranslation } from 'react-i18next'
import { Upload, X, CheckCircle, AlertCircle } from 'lucide-react'
import clsx from 'clsx'
import { filesApi } from '../../api/files'

interface Props {
  onUploadComplete: () => void
}

interface UploadItem {
  file: File
  status: 'pending' | 'uploading' | 'done' | 'error'
  error?: string
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / 1048576).toFixed(1)}MB`
}

export default function FileUploader({ onUploadComplete }: Props) {
  const { t } = useTranslation()
  const [items, setItems] = useState<UploadItem[]>([])
  const onUploadCompleteRef = useRef(onUploadComplete)
  onUploadCompleteRef.current = onUploadComplete

  const uploadFile = useCallback(async (file: File) => {
    setItems((prev) => prev.map((i) => i.file === file ? { ...i, status: 'uploading' } : i))
    try {
      await filesApi.upload(file)
      setItems((prev) => prev.map((i) => i.file === file ? { ...i, status: 'done' } : i))
      onUploadCompleteRef.current()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setItems((prev) => prev.map((i) => i.file === file ? { ...i, status: 'error', error: message } : i))
    }
  }, [])

  const onDrop = useCallback((accepted: File[]) => {
    const newItems: UploadItem[] = accepted.map((f) => ({ file: f, status: 'pending' }))
    setItems((prev) => [...prev, ...newItems])
    accepted.forEach(uploadFile)
  }, [uploadFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt', '.log'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/sql': ['.sql'],
      'text/x-sql': ['.sql'],
    },
  })

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all',
          isDragActive
            ? 'border-accent-green bg-accent-green/5 glow-green'
            : 'border-bg-border hover:border-accent-cyan/50 hover:bg-bg-card',
        )}
      >
        <input {...getInputProps()} />
        <Upload className={clsx('w-10 h-10 mx-auto mb-3', isDragActive ? 'text-accent-green' : 'text-text-muted')} />
        <p className="text-text-secondary text-sm">{t('files.dropzone')}</p>
        <p className="text-text-muted text-xs mt-1">{t('files.dropzoneHint')}</p>
      </div>

      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((item, i) => (
            <div key={i} className="flex items-center gap-3 bg-bg-card border border-bg-border rounded-lg px-4 py-2">
              <div className="flex-1 min-w-0">
                <div className="text-sm text-text-primary truncate">{item.file.name}</div>
                <div className="text-xs text-text-muted">{formatSize(item.file.size)}</div>
              </div>
              {item.status === 'uploading' && (
                <div className="w-4 h-4 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
              )}
              {item.status === 'done' && <CheckCircle className="w-4 h-4 text-accent-green" />}
              {item.status === 'error' && <span title={item.error}><AlertCircle className="w-4 h-4 text-accent-red" /></span>}
              <button onClick={() => setItems((p) => p.filter((_, j) => j !== i))}>
                <X className="w-4 h-4 text-text-muted hover:text-accent-red" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
