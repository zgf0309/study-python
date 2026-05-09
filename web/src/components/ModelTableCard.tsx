import { type ChangeEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Alert, App as AntApp, Button, Card, Flex, Input, Popover, Select, Space, Table, Tag, Typography } from 'antd'

import { FileDetailView, getFileKind } from './FileDetailView'

import {
  createChunkEmbeddings,
  createEmbeddings,
  createKnowledgeBase,
  fetchKnowledgeBases,
  fetchModels,
  fetchVectorizedFile,
  fetchVectorizedFiles,
  streamChat,
  uploadFileToMinio,
  vectorizeMinioFile,
  type ChatMessagePayload,
  type ChunkEmbeddingsResponse,
  type EmbeddingsResponse,
  type KnowledgeBaseRecord,
  type MinioUploadResponse,
  type ModelConfigRecord,
  type VectorizedFileRecord,
} from '../services/api'
import { unwrapList } from '../hooks/utils'

type ChatMessage = ChatMessagePayload & {
  id: string
}

const DEFAULT_SYSTEM_PROMPT = '你是一个严谨、友好的企业内网助手，请使用中文回答。'

function createMessage(role: ChatMessage['role'], content: string): ChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    content,
  }
}

export function ModelTableCard() {
  const { message } = AntApp.useApp()
  const [models, setModels] = useState<ModelConfigRecord[]>([])
  const [selectedModelId, setSelectedModelId] = useState<number>()
  const [input, setInput] = useState('')
  const [embeddingInput, setEmbeddingInput] = useState('')
  const [embeddingResult, setEmbeddingResult] = useState<EmbeddingsResponse | null>(null)
  const [embeddingLoading, setEmbeddingLoading] = useState(false)
  const [chunkText, setChunkText] = useState(
    'RAG 的基础流程通常包括：先将长文档切分为多个短文本片段，再使用 Embedding 模型将每个片段转换为向量，最后把向量和原文片段保存到向量数据库。用户提问时，也会先把问题转换为向量，然后检索最相似的文档片段，再把这些片段和问题一起交给大模型生成答案。',
  )
  const [chunkSize, setChunkSize] = useState(80)
  const [chunkOverlap, setChunkOverlap] = useState(20)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseRecord[]>([])
  const [selectedKnowledgeBaseId, setSelectedKnowledgeBaseId] = useState<number>()
  const [knowledgeBaseName, setKnowledgeBaseName] = useState('')
  const [knowledgeBasePopoverOpen, setKnowledgeBasePopoverOpen] = useState(false)
  const [chunkResult, setChunkResult] = useState<ChunkEmbeddingsResponse | null>(null)
  const [chunkLoading, setChunkLoading] = useState(false)
  const [fileUploadLoading, setFileUploadLoading] = useState(false)
  const [fileVectorLoading, setFileVectorLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<MinioUploadResponse | null>(null)
  const [vectorizedFiles, setVectorizedFiles] = useState<VectorizedFileRecord[]>([])
  const [fileVectorResult, setFileVectorResult] = useState<VectorizedFileRecord | null>(null)
  const [selectedFile, setSelectedFile] = useState<VectorizedFileRecord | null>(null)
  const [selectedFileLoading, setSelectedFileLoading] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loadingModels, setLoadingModels] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const selectedModel = useMemo(
    () => models.find((model) => model.id === selectedModelId),
    [models, selectedModelId],
  )

  const chatModels = useMemo(
    () => models.filter((model) => model.provider === 'openai-compatible'),
    [models],
  )

  const embeddingModel = useMemo(
    () => models.find((model) => model.provider === 'openai-compatible-embedding'),
    [models],
  )

  const modelOptions = useMemo(
    () =>
      chatModels.map((model) => ({
        label: `${model.name}${model.is_default ? '（默认）' : ''}`,
        value: model.id,
      })),
    [chatModels],
  )

  const knowledgeBaseOptions = useMemo(
    () => knowledgeBases.map((item) => ({
      label: item.name,
      value: item.id,
    })),
    [knowledgeBases],
  )

  const loadKnowledgeBases = useCallback(async () => {
    try {
      const res = await fetchKnowledgeBases()
      const result = unwrapList<KnowledgeBaseRecord>(res)
      const items = result?.items ?? []
      setKnowledgeBases(items)
      setSelectedKnowledgeBaseId((current) => current ?? items[0]?.id)
    } catch {
      void message.error('知识库列表加载失败。')
    }
  }, [message])

  const handleCreateKnowledgeBase = useCallback(async () => {
    const name = knowledgeBaseName.trim()
    if (!name) {
      void message.warning('请输入知识库名称。')
      return
    }
    try {
      const res = await createKnowledgeBase({ name })
      const wrapped = res as unknown as { data?: { data?: KnowledgeBaseRecord } }
      const record = wrapped.data?.data ?? (res as unknown as KnowledgeBaseRecord)
      setKnowledgeBases((items) => [record, ...items])
      setSelectedKnowledgeBaseId(record.id)
      setKnowledgeBaseName('')
      setKnowledgeBasePopoverOpen(false)
      void message.success('知识库已新增。')
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '知识库新增失败。')
    }
  }, [knowledgeBaseName, message])

  const loadModels = useCallback(async () => {
    setLoadingModels(true)
    try {
      const res = await fetchModels()
      const result = unwrapList<ModelConfigRecord>(res)
      const nextModels = result?.items ?? []
      const nextChatModels = nextModels.filter((item) => item.provider === 'openai-compatible')
      setModels(nextModels)
      setSelectedModelId((current) => current ?? nextChatModels.find((item) => item.is_default)?.id ?? nextChatModels[0]?.id)
    } catch {
      void message.error('模型配置加载失败，请检查后端服务。')
    } finally {
      setLoadingModels(false)
    }
  }, [message])

  const loadVectorizedFiles = useCallback(async () => {
    try {
      const res = await fetchVectorizedFiles()
      const result = unwrapList<VectorizedFileRecord>(res)
      setVectorizedFiles(result?.items ?? [])
    } catch {
      // 文件列表加载失败不影响模型对话主流程。
    }
  }, [])

  useEffect(() => {
    void loadModels()
    void loadKnowledgeBases()
    void loadVectorizedFiles()
    return () => abortRef.current?.abort()
  }, [loadKnowledgeBases, loadModels, loadVectorizedFiles])

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setStreaming(false)
  }, [])

  const sendMessage = useCallback(async () => {
    const content = input.trim()
    if (!content || streaming) return
    if (!selectedModelId) {
      void message.warning('请先选择模型。')
      return
    }

    const userMessage = createMessage('user', content)
    const assistantMessage = createMessage('assistant', '')
    const nextMessages = [...messages, userMessage]
    setMessages([...nextMessages, assistantMessage])
    setInput('')
    setStreaming(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      await streamChat(
        {
          model_id: selectedModelId,
          messages: [
            { role: 'system', content: DEFAULT_SYSTEM_PROMPT },
            ...nextMessages.map(({ role, content }) => ({ role, content })),
          ],
          temperature: 0.7,
        },
        {
          signal: controller.signal,
          onDelta: (delta) => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantMessage.id ? { ...item, content: item.content + delta } : item,
              ),
            )
          },
          onError: (errorMessage) => {
            void message.error(errorMessage)
          },
        },
      )
    } catch (error) {
      if (!controller.signal.aborted) {
        void message.error(error instanceof Error ? error.message : '模型调用失败。')
      }
    } finally {
      if (abortRef.current === controller) abortRef.current = null
      setStreaming(false)
    }
  }, [input, message, messages, selectedModelId, streaming])

  const testEmbeddings = useCallback(async () => {
    const content = embeddingInput.trim()
    if (!content) return
    if (!embeddingModel) {
      void message.warning('未找到可用的向量模型。')
      return
    }
    setEmbeddingLoading(true)
    try {
      const res = await createEmbeddings({
        model_id: embeddingModel.id,
        input: content,
      })
      const payload = res as unknown as { data?: { data?: EmbeddingsResponse } }
      setEmbeddingResult(payload.data?.data ?? null)
      void message.success('向量生成成功。')
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '向量模型调用失败。')
    } finally {
      setEmbeddingLoading(false)
    }
  }, [embeddingInput, embeddingModel, message])

  const testChunkEmbeddings = useCallback(async () => {
    const content = chunkText.trim()
    if (!content) return
    if (!embeddingModel) {
      void message.warning('未找到可用的向量模型。')
      return
    }
    setChunkLoading(true)
    try {
      const res = await createChunkEmbeddings({
        model_id: embeddingModel.id,
        text: content,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
      })
      const payload = res as unknown as { data?: { data?: ChunkEmbeddingsResponse } }
      setChunkResult(payload.data?.data ?? null)
      void message.success('切片并向量化成功。')
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '切片向量化失败。')
    } finally {
      setChunkLoading(false)
    }
  }, [chunkOverlap, chunkSize, chunkText, embeddingModel, message])

  const uploadSelectedFileToMinio = useCallback(async (file: File) => {
    setFileUploadLoading(true)
    try {
      const res = await uploadFileToMinio(file)
      const wrapped = res as unknown as { data?: { data?: MinioUploadResponse } }
      const result = wrapped.data?.data ?? (res as unknown as MinioUploadResponse)
      setUploadedFile(result)
      void message.success('文件已上传到 MinIO。')
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '文件上传到 MinIO 失败。')
    } finally {
      setFileUploadLoading(false)
    }
  }, [message])

  const handleFileInputChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      void uploadSelectedFileToMinio(file)
    }
    event.target.value = ''
  }, [uploadSelectedFileToMinio])

  const vectorizeUploadedFile = useCallback(async () => {
    if (!uploadedFile) {
      void message.warning('请先上传文件到 MinIO。')
      return
    }
    if (!embeddingModel) {
      void message.warning('未找到可用的向量模型。')
      return
    }
    if (!selectedKnowledgeBaseId) {
      void message.warning('请选择知识库。')
      return
    }
    setFileVectorLoading(true)
    try {
      const res = await vectorizeMinioFile({
        bucket: uploadedFile.bucket,
        object_name: uploadedFile.object_name,
        model_id: embeddingModel.id,
        knowledge_base_id: selectedKnowledgeBaseId,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
      })
      const wrapped = res as unknown as { data?: { data?: VectorizedFileRecord } }
      const result = wrapped.data?.data ?? (res as unknown as VectorizedFileRecord)
      setFileVectorResult(result)
      await loadVectorizedFiles()
      void message.success('文件已切片、向量化并保存到数据库。')
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '文件切片向量化失败。')
    } finally {
      setFileVectorLoading(false)
    }
  }, [chunkOverlap, chunkSize, embeddingModel, loadVectorizedFiles, message, selectedKnowledgeBaseId, uploadedFile])

  const firstEmbedding = embeddingResult?.data?.[0]?.embedding ?? []

  const openFileDetail = useCallback(async (record: VectorizedFileRecord) => {
    setSelectedFile(record)
    setSelectedFileLoading(true)
    try {
      const res = await fetchVectorizedFile(record.id)
      const wrapped = res as unknown as { data?: { data?: VectorizedFileRecord } }
      setSelectedFile(wrapped.data?.data ?? (res as unknown as VectorizedFileRecord))
    } catch (error) {
      void message.error(error instanceof Error ? error.message : '文件详情加载失败。')
    } finally {
      setSelectedFileLoading(false)
    }
  }, [message])

  const refreshSelectedFile = useCallback(async () => {
    if (!selectedFile) return
    await openFileDetail(selectedFile)
  }, [openFileDetail, selectedFile])
  
  return (
    <>
    { selectedFile ? (<FileDetailView
        file={selectedFile}
        loading={selectedFileLoading}
        onBack={() => setSelectedFile(null)}
        onRefresh={refreshSelectedFile}
      />)
    : (<Card
      title={
        <Flex gap={12} align="center" wrap="wrap">
          <h4 className="panel-title">模型对话</h4>
          {selectedModel ? <Tag color="processing">{selectedModel.model_name}</Tag> : null}
        </Flex>
      }
      extra={<Tag color="green">OpenAI 兼容流式接口</Tag>}
      style={{ borderRadius: '0 0 24px 24px' }}
    >
      <Alert
        type="info"
        showIcon
        className="hint"
        message="后端已写入默认 jusure-llm 对话模型和 qwen3-embed-4b 向量模型。对话通过 /api/chat/stream，向量通过 /api/embeddings。"
      />

      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Flex gap={12} align="center" wrap="wrap">
          <Select
            loading={loadingModels}
            placeholder="请选择模型"
            value={selectedModelId}
            options={modelOptions}
            onChange={setSelectedModelId}
            style={{ minWidth: 280, flex: 1 }}
          />
          <Button onClick={loadModels} loading={loadingModels}>刷新模型</Button>
        </Flex>

        {embeddingModel ? (
          <Alert
            type="success"
            showIcon
            message={`已启用向量模型：${embeddingModel.name}（${embeddingModel.model_name}）`}
          />
        ) : null}

        <div className="chat-window">
          {messages.length === 0 ? (
            <Typography.Text type="secondary">输入问题后开始与内网模型对话。</Typography.Text>
          ) : (
            messages.map((item) => (
              <div key={item.id} className={`chat-bubble ${item.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}>
                <Tag color={item.role === 'user' ? 'blue' : 'purple'}>{item.role === 'user' ? '我' : '助手'}</Tag>
                <Typography.Paragraph style={{ margin: '8px 0 0', whiteSpace: 'pre-wrap' }}>
                  {item.content || (item.role === 'assistant' && streaming ? '正在思考…' : '')}
                </Typography.Paragraph>
              </div>
            ))
          )}
        </div>

        <Input.TextArea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="请输入要发送给模型的问题"
          autoSize={{ minRows: 3, maxRows: 6 }}
          onPressEnter={(event) => {
            if (!event.shiftKey) {
              event.preventDefault()
              void sendMessage()
            }
          }}
        />

        <Flex justify="space-between" align="center" wrap="wrap" gap={12}>
          <Typography.Text type="secondary">Enter 发送，Shift + Enter 换行。</Typography.Text>
          <Space>
            <Button onClick={() => setMessages([])} disabled={streaming || messages.length === 0}>清空</Button>
            {streaming ? (
              <Button danger onClick={stopStreaming}>停止</Button>
            ) : (
              <Button type="primary" onClick={sendMessage} disabled={!input.trim()}>发送</Button>
            )}
          </Space>
        </Flex>

        <Card size="small" title="向量模型测试" styles={{ body: { paddingBottom: 16 } }}>
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            <Input.TextArea
              value={embeddingInput}
              onChange={(event) => setEmbeddingInput(event.target.value)}
              placeholder="请输入要向量化的文本"
              autoSize={{ minRows: 2, maxRows: 4 }}
            />
            <Flex justify="space-between" align="center" wrap="wrap" gap={12}>
              <Typography.Text type="secondary">
                {embeddingModel ? `调用模型：${embeddingModel.model_name}` : '暂无可用向量模型'}
              </Typography.Text>
              <Button
                type="primary"
                loading={embeddingLoading}
                disabled={!embeddingInput.trim() || !embeddingModel}
                onClick={testEmbeddings}
              >
                生成向量
              </Button>
            </Flex>
            {embeddingResult ? (
              <Alert
                type="info"
                showIcon
                message={`生成成功：维度 ${firstEmbedding.length}，返回条数 ${embeddingResult.data?.length ?? 0}`}
                description={`向量前 8 项：${firstEmbedding.slice(0, 8).join(', ')}`}
              />
            ) : null}
          </Space>
        </Card>

        <Card size="small" title="切片后批量向量化示例" styles={{ body: { paddingBottom: 16 } }}>
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            <Alert
              type="info"
              showIcon
              message="示例流程：长文本 → 按 chunk_size 切片 → 按 chunk_overlap 保留上下文重叠 → 批量调用 /api/embeddings/chunks 生成每个切片的向量。"
            />
            <Input.TextArea
              value={chunkText}
              onChange={(event) => setChunkText(event.target.value)}
              placeholder="请输入需要切片并向量化的长文本"
              autoSize={{ minRows: 4, maxRows: 8 }}
            />
            <Flex gap={12} align="center" wrap="wrap">
              <Space.Compact>
                <Button disabled>切片长度</Button>
                <Input
                  type="number"
                  min={1}
                  max={5000}
                  value={chunkSize}
                  onChange={(event) => setChunkSize(Number(event.target.value) || 80)}
                  style={{ width: 96 }}
                />
              </Space.Compact>
              <Space.Compact>
                <Button disabled>重叠长度</Button>
                <Input
                  type="number"
                  min={0}
                  max={chunkSize - 1}
                  value={chunkOverlap}
                  onChange={(event) => setChunkOverlap(Number(event.target.value) || 0)}
                  style={{ width: 96 }}
                />
              </Space.Compact>
              <Space.Compact>
                <Button disabled>知识库</Button>
                <Select
                  allowClear
                  placeholder="请选择知识库"
                  value={selectedKnowledgeBaseId}
                  options={knowledgeBaseOptions}
                  onChange={setSelectedKnowledgeBaseId}
                  style={{ width: 200 }}
                />
              </Space.Compact>
              <Popover
                trigger="click"
                open={knowledgeBasePopoverOpen}
                onOpenChange={setKnowledgeBasePopoverOpen}
                title="新建知识库"
                content={(
                  <Space direction="vertical" size={10} style={{ width: 260 }}>
                    <Input
                      autoFocus
                      placeholder="请输入知识库名称"
                      value={knowledgeBaseName}
                      onChange={(event) => setKnowledgeBaseName(event.target.value)}
                      onPressEnter={handleCreateKnowledgeBase}
                    />
                    <Flex justify="flex-end" gap={8}>
                      <Button size="small" onClick={() => setKnowledgeBasePopoverOpen(false)}>取消</Button>
                      <Button size="small" type="primary" onClick={handleCreateKnowledgeBase}>新增</Button>
                    </Flex>
                  </Space>
                )}
              >
                <Button>＋ 新建知识库</Button>
              </Popover>
              <input
                ref={fileInputRef}
                type="file"
                style={{ display: 'none' }}
                onChange={handleFileInputChange}
              />
              <Button
                loading={fileUploadLoading}
                onClick={() => fileInputRef.current?.click()}
              >
                上传文件到 MinIO
              </Button>
              <Button
                type="primary"
                loading={chunkLoading}
                disabled={!chunkText.trim() || !embeddingModel}
                onClick={testChunkEmbeddings}
              >
                切片并向量化
              </Button>
            </Flex>
            {uploadedFile ? (
              <Alert
                type="success"
                showIcon
                message={`MinIO 上传成功：${uploadedFile.filename}`}
                description={(
                  <Space direction="vertical" size={2}>
                    <Typography.Text type="secondary">Bucket：{uploadedFile.bucket}</Typography.Text>
                    <Typography.Text type="secondary">对象名：{uploadedFile.object_name}</Typography.Text>
                    <Flex gap={12} align="center">
                      <Typography.Link href={uploadedFile.presigned_url} target="_blank" rel="noreferrer">
                        打开临时访问链接
                      </Typography.Link>
                      <Button
                        type="primary"
                        loading={fileVectorLoading}
                        disabled={!embeddingModel || !selectedKnowledgeBaseId}
                        onClick={vectorizeUploadedFile}
                      >
                        文件切片并向量化
                      </Button>
                    </Flex>
                  </Space>
                )}
              />
            ) : null}
            {fileVectorResult ? (
              <Alert
                type="success"
                showIcon
                message={`数据库已保存文件：${fileVectorResult.filename}`}
                description={`知识库：${fileVectorResult.knowledge_base_name || '未关联'}；切片 ${fileVectorResult.chunk_count} 段，模型 ${fileVectorResult.embedding_model}，参数 ${fileVectorResult.chunk_size}/${fileVectorResult.chunk_overlap}`}
              />
            ) : null}
            {vectorizedFiles.length > 0 ? (
              <Table<VectorizedFileRecord>
                size="small"
                rowKey="id"
                pagination={{ pageSize: 5 }}
                dataSource={vectorizedFiles}
                columns={[
                  {
                    title: '文件名',
                    dataIndex: 'filename',
                    key: 'filename',
                    ellipsis: true,
                    render: (value: string, record) => (
                      <Button type="link" size="small" className="file-name-link" onClick={() => void openFileDetail(record)}>
                        {value}
                      </Button>
                    ),
                  },
                  {
                    title: '类型',
                    key: 'file_kind',
                    width: 90,
                    render: (_, record) => {
                      const kind = getFileKind(record)
                      const label = kind === 'image' ? '图片' : kind === 'audio' ? '音频' : kind === 'video' ? '视频' : '文档'
                      return <Tag>{label}</Tag>
                    },
                  },
                  { title: '切片数', dataIndex: 'chunk_count', key: 'chunk_count', width: 90 },
                  { title: '知识库', dataIndex: 'knowledge_base_name', key: 'knowledge_base_name', ellipsis: true },
                  { title: '向量模型', dataIndex: 'embedding_model', key: 'embedding_model', ellipsis: true },
                  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
                ]}
              />
            ) : null}
            {chunkResult ? (
              <Space direction="vertical" size={8} style={{ width: '100%' }}>
                <Alert
                  type="success"
                  showIcon
                  message={`切片完成：共 ${chunkResult.total_chunks} 段，模型 ${chunkResult.model ?? embeddingModel?.model_name}`}
                  description={`chunk_size=${chunkResult.chunk_size}，chunk_overlap=${chunkResult.chunk_overlap}`}
                />
                {chunkResult.chunks.slice(0, 5).map((chunk) => (
                  <Card key={chunk.index} size="small" type="inner" title={`切片 ${chunk.index + 1} · 向量维度 ${chunk.embedding_dim}`}>
                    <Typography.Paragraph ellipsis={{ rows: 2, expandable: true, symbol: '展开' }}>
                      {chunk.content}
                    </Typography.Paragraph>
                    <Typography.Text type="secondary">
                      位置：{chunk.start}-{chunk.end}；向量前 6 项：{chunk.embedding.slice(0, 6).join(', ')}
                    </Typography.Text>
                  </Card>
                ))}
              </Space>
            ) : null}
          </Space>
        </Card>
      </Space>
    </Card>)
    }
    
    </>
  )
}
