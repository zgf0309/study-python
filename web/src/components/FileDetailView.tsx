import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Button, Card, Empty, Flex, Input, Pagination, Select, Space, Switch, Tabs, Tag, Typography } from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import type { VectorizedFileRecord } from '../services/api'

type FileKind = 'document' | 'image' | 'audio' | 'video'
type FileChunk = NonNullable<VectorizedFileRecord['chunks']>[number]

interface FileDetailViewProps {
  file: VectorizedFileRecord
  loading?: boolean
  onBack: () => void
  onRefresh?: () => void
  onReparse?: () => void
}

const imageExt = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
const audioExt = ['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac']
const videoExt = ['mp4', 'webm', 'mov', 'm4v', 'avi', 'mkv']
const documentExt = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'md', 'csv', 'json']
const defaultPageSize = 5

function formatMediaTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return '00:00'
  const totalSeconds = Math.floor(seconds)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const restSeconds = totalSeconds % 60
  const twoDigits = (value: number) => String(value).padStart(2, '0')
  return hours > 0
    ? `${twoDigits(hours)}:${twoDigits(minutes)}:${twoDigits(restSeconds)}`
    : `${twoDigits(minutes)}:${twoDigits(restSeconds)}`
}

function extensionOf(filename: string) {
  return filename.split('.').pop()?.toLowerCase() ?? ''
}

function pageItems<T>(items: T[], page: number, pageSize = defaultPageSize) {
  const start = (page - 1) * pageSize
  return items.slice(start, start + pageSize)
}

function rebuildOriginalContent(chunks: NonNullable<VectorizedFileRecord['chunks']>) {
  const orderedChunks = [...chunks].sort((left, right) => left.index - right.index)
  let originalContent = ''
  let currentEnd = 0

  for (const chunk of orderedChunks) {
    if (chunk.start < currentEnd) {
      originalContent += chunk.content.slice(Math.max(0, currentEnd - chunk.start))
    } else {
      originalContent += chunk.content
    }
    currentEnd = Math.max(currentEnd, chunk.end)
  }

  return originalContent
}

export function getFileKind(file: Pick<VectorizedFileRecord, 'filename' | 'content_type'>): FileKind {
  const contentType = (file.content_type || '').toLowerCase()
  const ext = extensionOf(file.filename)
  if (contentType.startsWith('image/') || imageExt.includes(ext)) return 'image'
  if (contentType.startsWith('audio/') || audioExt.includes(ext)) return 'audio'
  if (contentType.startsWith('video/') || videoExt.includes(ext)) return 'video'
  if (documentExt.includes(ext)) return 'document'
  return 'document'
}

function fileIcon(kind: FileKind) {
  return kind === 'image' ? '🖼️' : kind === 'audio' ? '🎵' : kind === 'video' ? '🎬' : '📄'
}

function downloadLabel(kind: FileKind) {
  return kind === 'image' ? '下载原图' : kind === 'audio' ? '下载音频' : kind === 'video' ? '下载视频' : '下载原文'
}

function knowledgeType(kind: FileKind, index: number) {
  if (kind === 'image') return index === 0 ? '三元组知识' : '段落概要'
  return '原文语句'
}

function ChunkToolbar() {
  return (
    <div className="file-card-toolbar">
      <Button size="small" type="text">◎</Button>
      <Button size="small" type="text">↗</Button>
      <Switch size="small" defaultChecked />
    </div>
  )
}

function ChunkFilterHeader() {
  return (
    <Flex justify="space-between" align="center" className="detail-section-head chunk-filter-head">
      <Typography.Title level={5} style={{ margin: 0 }}>
        切片信息<Typography.Text type="secondary" className="section-help">?</Typography.Text>
      </Typography.Title>
      <Space>
        <Input.Search size="small" placeholder="搜索切片内容" style={{ width: 240 }} />
        <Select size="small" value="all" options={[{ label: '全部状态', value: 'all' }]} style={{ width: 120 }} />
      </Space>
    </Flex>
  )
}

function KnowledgePanel({
  file,
  kind,
  selectedChunkIndex,
}: {
  file: VectorizedFileRecord
  kind: FileKind
  selectedChunkIndex?: number
}) {
  const chunks = file.chunks ?? []
  const [page, setPage] = useState(1)
  const selectedChunk = typeof selectedChunkIndex === 'number'
    ? chunks.find((chunk) => chunk.index === selectedChunkIndex)
    : undefined
  const knowledgeChunks = selectedChunk ? [selectedChunk] : chunks
  const visibleChunks = pageItems(knowledgeChunks, page)

  useEffect(() => {
    setPage(1)
  }, [selectedChunkIndex])

  return (
    <aside className="knowledge-panel">
      <Flex justify="space-between" align="center" className="detail-section-head">
        <Typography.Title level={5} style={{margin: 0}}>
          切片知识点（{selectedChunk ? `#${selectedChunk.index + 1}` : Math.max(chunks.length, file.chunk_count || 0)}）
        </Typography.Title>
        <Button size="small">＋ 新建</Button>
      </Flex>
      {selectedChunk ? (
        <Typography.Text type="secondary" className="knowledge-current">
          当前显示切片 #{selectedChunk.index + 1} 对应知识点
        </Typography.Text>
      ) : null}
      <Space direction="vertical" size={10} className="knowledge-list">
        {knowledgeChunks.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无切片知识点" />
        ) : visibleChunks.map((chunk) => (
          <Card key={chunk.index} size="small" className="knowledge-card">
            <Typography.Paragraph ellipsis={{ rows: 3 }} className="knowledge-text">
              {chunk.content}
            </Typography.Paragraph>
            <Flex justify="flex-end" align="center" gap={10}>
              <Typography.Text type="secondary">类型：{knowledgeType(kind, chunk.index)}</Typography.Text>
              <Button type="text" size="small">↗</Button>
              <Button type="text" size="small">🗑</Button>
            </Flex>
          </Card>
        ))}
      </Space>
      {knowledgeChunks.length > defaultPageSize ? (
        <Pagination
          className="detail-pagination"
          current={page}
          pageSize={defaultPageSize}
          total={knowledgeChunks.length}
          size="small"
          showSizeChanger={false}
          showTotal={(total, range) => `第 ${range[0]}-${range[1]} 条 / 共 ${total} 条，每页 ${defaultPageSize} 条`}
          onChange={setPage}
        />
      ) : null}
    </aside>
  )
}

function ChunkCard({
  file,
  kind,
  videoCurrentTime = 0,
  videoFrameUrl,
}: {
  file: VectorizedFileRecord
  kind: FileKind
  videoCurrentTime?: number
  videoFrameUrl?: string
}) {
  const chunks = file.chunks ?? []
  const first = chunks[0]
  const previewUrl = file.presigned_url || file.public_url || ''

  return (
    <Card className="active-chunk-card" loading={false}>
      <ChunkToolbar />
      <Typography.Text strong className="chunk-number">#1 · 原文切片 · {first?.length ?? file.size}字符</Typography.Text>
      {kind === 'image' && previewUrl ? <img className="image-preview" src={previewUrl} alt={file.filename} /> : null}
      {kind === 'image' ? (
        <div className="image-caption">
          <Typography.Text>🔷 暂无标题</Typography.Text>
          <Typography.Text type="secondary">暂无详细信息</Typography.Text>
        </div>
      ) : (
        <>
          {kind === 'video' ? (
            <div className="video-frame-info">
              <Flex justify="space-between" align="center" className="video-frame-meta">
                <Typography.Text strong>当前播放位置</Typography.Text>
                <Tag color="processing">{formatMediaTime(videoCurrentTime)}</Tag>
              </Flex>
              {videoFrameUrl ? (
                <img className="video-frame-image" src={videoFrameUrl} alt={`当前视频帧 ${formatMediaTime(videoCurrentTime)}`} />
              ) : (
                <div className="video-frame-empty">
                  <Typography.Text type="secondary">播放视频后显示当前视频帧</Typography.Text>
                </div>
              )}
            </div>
          ) : null}
          <Typography.Paragraph className="chunk-content">
            {first?.content || '暂无可展示的切片文本。'}
          </Typography.Paragraph>
        </>
      )}
    </Card>
  )
}

function DocumentOriginal({ file }: { file: VectorizedFileRecord }) {
  const chunks = file.chunks ?? []
  const originalContent = useMemo(() => file.original_content ?? rebuildOriginalContent(chunks), [chunks, file.original_content])

  return (
    <section className="document-original">
      <Typography.Title level={5}>原文对照</Typography.Title>
      <div className="doc-tip">ⓘ 通过点击右侧切片，快速查看对应原文内容</div>
      <div className="doc-paper">
        <Typography.Title level={3}>{file.filename.replace(/\.[^.]+$/, '') || '文档内容'}</Typography.Title>
        {
          originalContent ? (
            <div className="markdown-source">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{originalContent}</ReactMarkdown>
            </div>
          ) : (
            <Empty description="暂无 Markdown 原文" />
          )
        }
      </div>
    </section>
  )
}

function ChunkList({
  file,
  selectedChunkIndex,
  onSelectChunk,
}: {
  file: VectorizedFileRecord
  selectedChunkIndex?: number
  onSelectChunk: (chunk: FileChunk) => void
}) {
  const chunks = file.chunks ?? []
  const [page, setPage] = useState(1)
  const [activeTab, setActiveTab] = useState('all')
  const filteredChunks = activeTab === 'custom' ? [] : chunks
  const visibleChunks = pageItems(filteredChunks, page)

  return (
    <section className="chunk-list-panel">
      <Flex justify="space-between" align="center" className="detail-section-head">
        <Typography.Title level={5} style={{margin: 0}}>
          切片信息<Typography.Text type="secondary" className="section-help">?</Typography.Text>
        </Typography.Title>
        <Space>
          <Input.Search size="small" placeholder="搜索切片内容" style={{ width: 150 }} />
          <Select size="small" value="all" options={[{ label: '全部状态', value: 'all' }]} style={{ width: 110 }} />
          <Button size="small">＋ 新建</Button>
        </Space>
      </Flex>
      <Tabs
        activeKey={activeTab}
        className="chunk-tabs"
        items={[
          { key: 'all', label: `全部 (${chunks.length})` },
          { key: 'original', label: `原文切片 (${chunks.length})` },
          { key: 'custom', label: '自定义切片 (0)' },
        ]}
        onChange={(key) => {
          setActiveTab(key)
          setPage(1)
        }}
      />
      <Space direction="vertical" size={10} className="chunk-list">
        {filteredChunks.length === 0 ? <Empty description={activeTab === 'custom' ? '暂无自定义切片' : '暂无切片信息'} /> : visibleChunks.map((chunk) => (
          <Card
            key={chunk.index}
            size="small"
            className={chunk.index === selectedChunkIndex ? 'chunk-row chunk-row-active' : 'chunk-row'}
            hoverable
            onClick={() => onSelectChunk(chunk)}
          >
            <ChunkToolbar />
            <Typography.Text strong>#{chunk.index + 1} · 原文切片 · {chunk.length}字符</Typography.Text>
            <Typography.Paragraph ellipsis={{ rows: 2 }} className="chunk-row-text">{chunk.content}</Typography.Paragraph>
            <Tag color={chunk.index === selectedChunkIndex ? 'processing' : 'success'}>
              {chunk.index === selectedChunkIndex ? '当前选中' : '已启用'}
            </Tag>
          </Card>
        ))}
      </Space>
      {filteredChunks.length > defaultPageSize ? (
        <Pagination
          className="detail-pagination"
          current={page}
          pageSize={defaultPageSize}
          total={filteredChunks.length}
          size="small"
          showSizeChanger={false}
          onChange={setPage}
        />
      ) : null}
    </section>
  )
}

export function FileDetailView({ file, loading, onBack, onRefresh, onReparse }: FileDetailViewProps) {
  const kind = getFileKind(file)
  const previewUrl = file.presigned_url || file.public_url || ''
  const chunks = file.chunks ?? []
  const [selectedChunkIndex, setSelectedChunkIndex] = useState<number | undefined>(chunks[0]?.index)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const lastFrameCaptureTimeRef = useRef(-1)
  const [videoCurrentTime, setVideoCurrentTime] = useState(0)
  const [videoFrameUrl, setVideoFrameUrl] = useState('')

  useEffect(() => {
    setSelectedChunkIndex(file.chunks?.[0]?.index)
  }, [file.id, file.chunks])

  useEffect(() => {
    setVideoCurrentTime(0)
    setVideoFrameUrl('')
    lastFrameCaptureTimeRef.current = -1
  }, [file.id])

  const captureVideoFrame = useCallback(() => {
    const video = videoRef.current
    if (!video || video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) return

    const currentTime = video.currentTime || 0
    setVideoCurrentTime(currentTime)

    if (Math.abs(currentTime - lastFrameCaptureTimeRef.current) < 0.45) return
    lastFrameCaptureTimeRef.current = currentTime

    const canvas = document.createElement('canvas')
    const maxWidth = 360
    const scale = Math.min(1, maxWidth / video.videoWidth)
    canvas.width = Math.max(1, Math.round(video.videoWidth * scale))
    canvas.height = Math.max(1, Math.round(video.videoHeight * scale))
    const context = canvas.getContext('2d')
    if (!context) return

    try {
      context.drawImage(video, 0, 0, canvas.width, canvas.height)
      setVideoFrameUrl(canvas.toDataURL('image/jpeg', 0.82))
    } catch {
      // 如果对象存储未开启跨域，canvas 可能被浏览器安全策略拦截；此时保留时间显示即可。
      setVideoFrameUrl('')
    }
  }, [])

  return (
    <div className="file-detail-page">
      <header className="file-detail-header">
        <Flex align="center" gap={10}>
          <Button type="text" onClick={onBack}>‹</Button>
          <span className={`file-kind-icon file-kind-${kind}`}>{fileIcon(kind)}</span>
          <Typography.Text strong>{file.filename}</Typography.Text>
        </Flex>
        <Space>
          <Button href={previewUrl} target="_blank" disabled={!previewUrl}>⇩ {downloadLabel(kind)}</Button>
          <Button>☷ 配置详情</Button>
          <Button>🎯 命中测试</Button>
          {onReparse ? <Button type="primary" loading={loading} onClick={onReparse}>重新解析</Button> : null}
          {onRefresh ? <Button loading={loading} onClick={onRefresh}>刷新</Button> : null}
        </Space>
      </header>

      {kind === 'document' ? (
        <main className="document-detail-layout">
          <DocumentOriginal file={file} />
          <ChunkList
            file={file}
            selectedChunkIndex={selectedChunkIndex}
            onSelectChunk={(chunk) => setSelectedChunkIndex(chunk.index)}
          />
          <KnowledgePanel file={file} kind={kind} selectedChunkIndex={selectedChunkIndex} />
        </main>
      ) : (
        <main className="media-detail-layout">
          <section className="media-main-panel">
            {kind === 'audio' ? (
              <>
                <Typography.Title level={5}>音频源文件</Typography.Title>
                <div className="audio-player-shell">
                  {previewUrl ? <audio src={previewUrl} controls /> : <Typography.Text type="secondary">暂无音频预览地址</Typography.Text>}
                </div>
                <ChunkFilterHeader />
              </>
            ) : null}
            {kind === 'video' ? (
              <>
                <Typography.Title level={5}>视频源文件</Typography.Title>
                <div className="video-player-shell">
                  {previewUrl ? (
                    <video
                      ref={videoRef}
                      src={previewUrl}
                      controls
                      onLoadedData={captureVideoFrame}
                      onSeeked={captureVideoFrame}
                      onTimeUpdate={captureVideoFrame}
                    />
                  ) : <Typography.Text type="secondary">暂无视频预览地址</Typography.Text>}
                </div>
                <ChunkFilterHeader />
              </>
            ) : null}
            <ChunkCard file={file} kind={kind} videoCurrentTime={videoCurrentTime} videoFrameUrl={videoFrameUrl} />
          </section>
          <KnowledgePanel file={file} kind={kind} selectedChunkIndex={selectedChunkIndex} />
        </main>
      )}
    </div>
  )
}
