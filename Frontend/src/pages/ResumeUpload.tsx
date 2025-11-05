import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileText, Loader2, CheckCircle } from 'lucide-react';
import { uploadResumeAndMatchJobs, saveMatchedJobs, saveResume, getResumes } from '@/lib/api';
import { toast } from 'sonner';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const ResumeUpload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [savedResumes] = useState(getResumes());

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
      } else {
        toast.error('Please upload a PDF file');
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        toast.error('Please upload a PDF file');
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setIsUploading(true);
    try {
      // Show processing page
      navigate('/processing');
      
      // Upload resume and get matched jobs
      const jobs = await uploadResumeAndMatchJobs(file);
      
      // Save resume to local storage
      const fileUrl = URL.createObjectURL(file);
      const fileBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      const savedResume = saveResume(file.name, fileUrl, fileBase64);
      
      // Save matched jobs with resume ID
      saveMatchedJobs(jobs, savedResume.id);
      
      toast.success(`Found ${jobs.length} matching jobs!`);
      
      // Redirect to dashboard
      setTimeout(() => {
        navigate('/dashboard/resumes');
      }, 1500);
    } catch (error) {
      navigate('/resume-upload');
      toast.error('Failed to process resume. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectSavedResume = async (resumeId: string) => {
    const resume = savedResumes.find(r => r.id === resumeId);
    if (!resume) return;
    try {
      setIsUploading(true);
      navigate('/processing');
      let fileToProcess: File | null = null;
      if (resume.fileBase64) {
        const res = await fetch(resume.fileBase64);
        const blob = await res.blob();
        fileToProcess = new File([blob], resume.filename, { type: 'application/pdf' });
      } else if (resume.fileUrl) {
        const res = await fetch(resume.fileUrl);
        const blob = await res.blob();
        fileToProcess = new File([blob], resume.filename, { type: 'application/pdf' });
      }
      if (!fileToProcess) throw new Error('Could not load saved resume');
      const jobs = await uploadResumeAndMatchJobs(fileToProcess);
      saveMatchedJobs(jobs, resume.id);
      toast.success(`Found ${jobs.length} matching jobs!`);
      setTimeout(() => {
        navigate('/dashboard/resumes');
      }, 1200);
    } catch (e) {
      navigate('/resume-upload');
      toast.error('Failed to re-process saved resume.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background p-4 md:p-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8 animate-fade-in">
            <h1 className="text-3xl font-bold mb-2">Upload Your Resume</h1>
            <p className="text-muted-foreground">
              Upload your resume to get personalized job matches
            </p>
          </div>

          {savedResumes.length > 0 && (
            <Card className="mb-6 animate-fade-in">
              <CardHeader>
                <CardTitle>Previous Resumes</CardTitle>
                <CardDescription>Select a previously uploaded resume</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {savedResumes.map((resume) => (
                  <div
                    key={resume.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-secondary/50 transition-colors cursor-pointer"
                    onClick={() => handleSelectSavedResume(resume.id)}
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">{resume.filename}</p>
                        <p className="text-sm text-muted-foreground">
                          Uploaded {new Date(resume.uploadedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <CheckCircle className="h-5 w-5 text-accent" />
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          <Card className="animate-slide-up">
            <CardHeader>
              <CardTitle>Upload New Resume</CardTitle>
              <CardDescription>
                Supported format: PDF (Max size: 10MB)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
                  isDragging
                    ? 'border-primary bg-primary-light'
                    : 'border-border hover:border-primary/50'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
              >
                {file ? (
                  <div className="space-y-4">
                    <FileText className="h-16 w-16 mx-auto text-accent" />
                    <div>
                      <p className="font-medium text-lg">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <div className="flex gap-3 justify-center">
                      <Button
                        onClick={handleUpload}
                        disabled={isUploading}
                        size="lg"
                      >
                        {isUploading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-4 w-4" />
                            Process Resume
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setFile(null)}
                        disabled={isUploading}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="h-16 w-16 mx-auto text-muted-foreground" />
                    <div>
                      <p className="text-lg font-medium mb-2">
                        Drag and drop your resume here
                      </p>
                      <p className="text-sm text-muted-foreground mb-4">
                        or click to browse
                      </p>
                    </div>
                    <Button asChild variant="outline">
                      <label htmlFor="resume-upload" className="cursor-pointer">
                        Select File
                        <input
                          id="resume-upload"
                          type="file"
                          accept=".pdf"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                      </label>
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="mt-6 text-center">
            <Button variant="ghost" onClick={() => navigate('/dashboard')}>
              Skip for now
            </Button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default ResumeUpload;
