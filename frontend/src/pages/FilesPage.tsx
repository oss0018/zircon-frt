import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import FileUploader from '../components/files/FileUploader'
import FileList from '../components/files/FileList'
import { filesApi, type FileRecord } from '../api/files'

export default function FilesPage() {
  const { t } = useTranslation()
  const [files, setFiles] = useState<FileRecord[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  const loadFiles = useCallback(async () => {
    setLoading(true)
    try {
      const res = await filesApi.list()
      setFiles(res.data.items)
      setTotal(res.data.total)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadFiles() }, [loadFiles])

  const handleDelete = async (id: number) => {
    if (!window.confirm(t('files.deleteConfirm'))) return
    await filesApi.delete(id)
    loadFiles()
  }

  const handleRename = async (id: number, current: string) => {
    const newName = window.prompt('New filename:', current)
    if (newName && newName !== current) {
      await filesApi.rename(id, newName)
      loadFiles()
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-text-primary">{t('files.title')}</h1>
        <span className="text-text-muted text-sm font-mono">{total} files</span>
      </div>

      <FileUploader onUploadComplete={loadFiles} />

      <div className="bg-bg-card border border-bg-border rounded-xl">
        {loading ? (
          <div className="text-center py-16 text-text-muted">
            <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            {t('common.loading')}
          </div>
        ) : (
          <FileList files={files} onDelete={handleDelete} onRename={handleRename} />
        )}
      </div>
    </div>
  )
}
