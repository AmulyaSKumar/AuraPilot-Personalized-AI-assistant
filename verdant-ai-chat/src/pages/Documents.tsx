import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Trash2, RefreshCw, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { ChatSidebar } from '@/components/ChatSidebar';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/store';
import { documentAPI } from '@/lib/api';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface Document {
  id: number;
  filename: string;
  file_size: number | null;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count: number;
  error_message?: string;
  created_at: string;
}

export default function Documents() {
  const { token, checkAuth } = useAuth();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (!token) {
      navigate('/login');
    } else {
      loadDocuments();
    }
  }, [token, navigate]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await documentAPI.list();
      const docs = Array.isArray(response.data) ? response.data : [];
      setDocuments(docs);
    } catch (err) {
      console.error('Error loading documents:', err);
      toast.error('Failed to load documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const { data } = await documentAPI.upload(file);
        setDocuments(prev => [data, ...prev]);
        toast.success(`${file.name} uploaded successfully`);
      }
    } catch (err: any) {
      console.error('Error uploading document:', err);
      toast.error(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number, filename: string) => {
    if (!confirm(`Delete "${filename}"?`)) return;
    try {
      await documentAPI.delete(id);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      toast.success('Document deleted');
    } catch (err) {
      console.error('Error deleting document:', err);
      toast.error('Failed to delete document');
    }
  };

  const handleReindex = async (id: number) => {
    try {
      await documentAPI.reindex(id);
      toast.success('Document reindexing started');
      loadDocuments();
    } catch (err) {
      console.error('Error reindexing document:', err);
      toast.error('Failed to reindex document');
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleUpload(e.dataTransfer.files);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'indexed':
        return <CheckCircle className="h-4 w-4 text-primary" />;
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4 text-muted-foreground animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background flex">
      <ChatSidebar />
      <main className="flex-1 md:ml-64 p-6 md:p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Documents</h1>
          <p className="text-muted-foreground mb-8">
            Upload and manage your documents for AI-powered search and analysis.
          </p>

          {/* Upload Area */}
          <div
            className={cn(
              "relative border-2 border-dashed rounded-2xl p-8 mb-8 transition-colors",
              dragActive ? "border-primary bg-primary/5" : "border-border",
              uploading && "opacity-50 pointer-events-none"
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-upload"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf,.txt,.md"
              multiple
              onChange={(e) => handleUpload(e.target.files)}
              disabled={uploading}
            />
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <p className="text-lg font-medium mb-1">
                {uploading ? 'Uploading...' : 'Drop files here or click to upload'}
              </p>
              <p className="text-muted-foreground text-sm">
                Supports PDF, TXT, MD files
              </p>
            </div>
          </div>

          {/* Documents List */}
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading documents...
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No documents yet</p>
                <p className="text-sm text-muted-foreground">Upload your first document to get started</p>
              </div>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center gap-4 p-4 bg-card border border-border rounded-xl"
                >
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{doc.filename}</p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>{formatFileSize(doc.file_size || 0)}</span>
                      <span>•</span>
                      <span>{doc.chunk_count} chunks</span>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(doc.processing_status)}
                        <span className="capitalize">{doc.processing_status}</span>
                      </div>
                    </div>
                    {doc.error_message && (
                      <p className="text-sm text-destructive mt-1">{doc.error_message}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {doc.processing_status === 'failed' && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleReindex(doc.id)}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
