import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getResumesSortedByLatest, deleteResume } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { FileText, Upload, Briefcase, Calendar, ChevronRight, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { toast } from '@/hooks/use-toast';

const Resumes = () => {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState(getResumesSortedByLatest());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [resumeToDelete, setResumeToDelete] = useState<{ id: string; filename: string; jobCount: number } | null>(null);

  const handleDeleteResume = () => {
    if (!resumeToDelete) return;
    
    deleteResume(resumeToDelete.id);
    setResumes(getResumesSortedByLatest());
    setDeleteDialogOpen(false);
    setResumeToDelete(null);
    
    toast({
      title: "Resume deleted",
      description: `${resumeToDelete.filename} and all ${resumeToDelete.jobCount} associated jobs have been deleted.`,
    });
  };

  const openDeleteDialog = (e: React.MouseEvent, resume: { id: string; filename: string; jobCount: number }) => {
    e.stopPropagation();
    setResumeToDelete(resume);
    setDeleteDialogOpen(true);
  };

  if (resumes.length === 0) {
    return (
      <div className="text-center py-12 animate-fade-in">
        <Upload className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h2 className="text-2xl font-bold mb-2">No Resumes Yet</h2>
        <p className="text-muted-foreground mb-6">
          Upload your resume to get personalized job matches
        </p>
        <Button onClick={() => navigate('/resume-upload')} size="lg">
          <Upload className="mr-2 h-4 w-4" />
          Upload Resume
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Resumes</h1>
          <p className="text-muted-foreground">
            {resumes.length} {resumes.length === 1 ? 'resume' : 'resumes'} uploaded
          </p>
        </div>
        <Button onClick={() => navigate('/resume-upload')}>
          <Upload className="mr-2 h-4 w-4" />
          Upload New Resume
        </Button>
      </div>

      {/* Resumes Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {resumes.map((resume) => (
          <Card 
            key={resume.id} 
            className="group hover:shadow-card-hover transition-all duration-300 cursor-pointer border-2 hover:border-primary"
            onClick={() => navigate(`/dashboard/resumes/${resume.id}/jobs`)}
          >
            <CardHeader className="space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="h-5 w-5 text-primary flex-shrink-0" />
                    <CardTitle className="text-lg truncate">{resume.filename}</CardTitle>
                  </div>
                  <CardDescription className="flex items-center gap-2">
                    <Calendar className="h-3 w-3" />
                    <span className="text-xs">
                      Updated {formatDistanceToNow(new Date(resume.lastExtraction), { addSuffix: true })}
                    </span>
                  </CardDescription>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all flex-shrink-0" />
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-primary/10">
                    <Briefcase className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-primary">{resume.jobCount}</p>
                    <p className="text-xs text-muted-foreground">Matched Jobs</p>
                  </div>
                </div>
                <Badge variant="secondary" className="text-xs">
                  View Jobs
                </Badge>
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1 group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/dashboard/resumes/${resume.id}/jobs`);
                  }}
                >
                  View All Jobs
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="hover:bg-destructive hover:text-destructive-foreground transition-colors border-destructive/30"
                  onClick={(e) => openDeleteDialog(e, resume)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the resume <strong>"{resumeToDelete?.filename}"</strong> and all <strong>{resumeToDelete?.jobCount} job{resumeToDelete?.jobCount !== 1 ? 's' : ''}</strong> associated with it. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteResume}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Resumes;
