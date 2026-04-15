import { useTranslation } from 'react-i18next'
import { Download, Trash2, PenLine, FileText } from 'lucide-react'
import type { FileRecord } from '../../api/files'
import { filesApi } from '../../api/files'

interface Props {
  files: FileRecord[]
  onDelete: (id: number) => void
  onRename: (id: number, current: string) => void
}

function StatusBadge({ file }: { file: FileRecord }) {
  const { t } = useTranslation()
  if (file.quarantined) {
    return <span className="px-2 py-0.5 bg-accent-red/15 text-accent-red text-xs rounded font-mono">{t('files.quarantined')}</span>
  }
  if (file.indexed) {
    return <span className="px-2 py-0.5 bg-accent-green/15 text-accent-green text-xs rounded font-mono">{t('files.indexed')}</span>
  }
  return <span className="px-2 py-0.5 bg-accent-cyan/15 text-accent-cyan text-xs rounded font-mono">{t('files.processing')}</span>
}

function formatSize(bytes: number | null): string {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / 1048576).toFixed(1)}MB`
}

export default function FileList({ files, onDelete, onRename }: Props) {
  const { t } = useTranslation()

  const handleDownload = async (file: FileRecord) => {
    const res = await filesApi.download(file.id)
    const url = URL.createObjectURL(res.data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.filename
    a.click()
    URL.revokeObjectURL(url)
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-16 text-text-muted">
        <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p>{t('files.noFiles')}</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-bg-border text-text-muted text-xs uppercase tracking-wider">
            <th className="text-left py-3 px-4">{t('files.name')}</th>
            <th className="text-left py-3 px-4">{t('files.type')}</th>
            <th className="text-left py-3 px-4">{t('files.size')}</th>
            <th className="text-left py-3 px-4">{t('files.date')}</th>
            <th className="text-left py-3 px-4">{t('files.status')}</th>
            <th className="text-left py-3 px-4">{t('files.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id} className="border-b border-bg-border hover:bg-white/[0.02] transition-colors">
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-accent-cyan shrink-0" />
                  <span className="text-text-primary font-medium truncate max-w-[200px]">{file.filename}</span>
                </div>
              </td>
              <td className="py-3 px-4 text-text-secondary font-mono">{file.file_type || '—'}</td>
              <td className="py-3 px-4 text-text-secondary">{formatSize(file.size_bytes)}</td>
              <td className="py-3 px-4 text-text-muted">{new Date(file.created_at).toLocaleDateString()}</td>
              <td className="py-3 px-4"><StatusBadge file={file} /></td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <button onClick={() => handleDownload(file)} className="p-1 text-text-muted hover:text-accent-cyan transition-colors" title={t('files.download')}>
                    <Download className="w-4 h-4" />
                  </button>
                  <button onClick={() => onRename(file.id, file.filename)} className="p-1 text-text-muted hover:text-accent-green transition-colors" title={t('files.rename')}>
                    <PenLine className="w-4 h-4" />
                  </button>
                  <button onClick={() => onDelete(file.id)} className="p-1 text-text-muted hover:text-accent-red transition-colors" title={t('files.delete')}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
