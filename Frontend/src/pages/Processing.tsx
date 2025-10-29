import { useEffect } from 'react';
import { Loader2, FileSearch, Brain, CheckCircle } from 'lucide-react';

const Processing = () => {
  useEffect(() => {
    // This page is only shown during the actual processing
    // Navigation to dashboard happens in ResumeUpload component
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-primary-light/50 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center space-y-8 animate-fade-in">
        <div className="relative">
          <div className="h-32 w-32 mx-auto relative">
            <Loader2 className="h-32 w-32 text-primary animate-spin" />
            <Brain className="h-16 w-16 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary" />
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-3xl font-bold">Analyzing Your Resume</h2>
          <p className="text-muted-foreground text-lg">
            Our AI is matching your skills with thousands of jobs
          </p>
        </div>

        <div className="space-y-4 text-left bg-card p-6 rounded-lg shadow-card">
          <div className="flex items-start gap-3 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <CheckCircle className="h-5 w-5 text-accent mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Extracting Skills</p>
              <p className="text-sm text-muted-foreground">
                Identifying your technical and soft skills
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <FileSearch className="h-5 w-5 text-primary mt-0.5 flex-shrink-0 animate-pulse" />
            <div>
              <p className="font-medium">Searching Job Database</p>
              <p className="text-sm text-muted-foreground">
                Scanning thousands of job listings
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 animate-slide-up opacity-50" style={{ animationDelay: '0.6s' }}>
            <Brain className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Calculating Match Scores</p>
              <p className="text-sm text-muted-foreground">
                Ranking jobs by compatibility
              </p>
            </div>
          </div>
        </div>

        <p className="text-sm text-muted-foreground">
          This usually takes 10-30 seconds...
        </p>
      </div>
    </div>
  );
};

export default Processing;
