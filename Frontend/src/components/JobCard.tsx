import { Job } from '@/types/job';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { 
  Building2, 
  MapPin, 
  DollarSign, 
  Calendar,
  Briefcase,
  ExternalLink,
  Award,
  CheckCircle,
  Clock,
  FileText,
} from 'lucide-react';
import { saveJobToLocalStorage, getAppliedJobsFromLocalStorage } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';

interface JobCardProps {
  job: Job;
  showMatchScore?: boolean;
  appliedMode?: boolean;
  onCardClick?: (job: Job) => void;
  resumeContext?: {
    resumeId?: string;
    resumeFilename?: string;
    batchId?: string;
    extractionDate?: string;
  };
  appliedMetadata?: {
    appliedAt?: string;
    resumeName?: string;
  };
}

export function JobCard({ job, showMatchScore = true, appliedMode = false, onCardClick, resumeContext, appliedMetadata }: JobCardProps) {
  const handleApply = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    window.open(job.url, '_blank');
    saveJobToLocalStorage(job, {
      resumeId: resumeContext?.resumeId ?? job.resumeId,
      resumeFilename: resumeContext?.resumeFilename ?? job.resumeFilename,
      batchId: resumeContext?.batchId ?? job.batchId,
      extractionDate: resumeContext?.extractionDate ?? job.extractionDate,
    });
    toast.success('Job saved to Applied Jobs!');
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-accent';
    if (score >= 60) return 'text-primary';
    return 'text-muted-foreground';
  };

  const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 80) return 'default';
    if (score >= 60) return 'secondary';
    return 'outline';
  };

  const isAlreadyApplied = getAppliedJobsFromLocalStorage().some(j => j.job_id === job.job_id);

  const jobWithMeta = job as Job & {
    appliedAt?: string;
    resumeFilename?: string;
  };

  const appliedInfo = appliedMetadata ?? (appliedMode
    ? {
        appliedAt: jobWithMeta.appliedAt,
        resumeName: jobWithMeta.resumeFilename,
      }
    : undefined);

  return (
    <Card className="group hover:shadow-card-hover transition-all duration-300 animate-fade-in cursor-pointer" onClick={() => onCardClick?.(job)}>
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors">
              {job.title}
            </h3>
            <div className="flex items-center gap-2 mt-2 text-muted-foreground">
              <Building2 className="h-4 w-4" />
              <span className="font-medium">{job.company}</span>
            </div>
          </div>
          {(appliedMode || isAlreadyApplied) && (
            <div className="flex items-center gap-1">
              <div className="bg-accent text-accent-foreground rounded-full p-2 shadow-lg">
                <CheckCircle className="h-4 w-4" />
              </div>
            </div>
          )}
          {showMatchScore && job.hybridScore !== undefined && (
            <div className="flex flex-col items-end gap-1">
              <Badge variant={getScoreBadgeVariant(job.hybridScore)} className="text-sm">
                {job.rank && `#${job.rank}`}
              </Badge>
              <div className={`text-2xl font-bold ${getScoreColor(job.hybridScore)}`}>
                {job.hybridScore.toFixed(0)}%
              </div>
              <span className="text-xs text-muted-foreground">Match</span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <MapPin className="h-4 w-4" />
            <span>{job.location}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Briefcase className="h-4 w-4" />
            <span>{job.job_type}</span>
          </div>
          {job.salary && job.salary !== 'Not specified' && (
            <div className="flex items-center gap-1.5">
              <DollarSign className="h-4 w-4" />
              <span>{job.salary}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4" />
            <span>{new Date(job.posted_date).toLocaleDateString()}</span>
          </div>
        </div>

        <p className="text-sm text-foreground/80 line-clamp-3">
          {job.description}
        </p>

        {appliedInfo && (appliedInfo.appliedAt || appliedInfo.resumeName) && (
          <div className="flex flex-wrap items-center gap-3 rounded-lg border border-secondary/50 bg-secondary/40 p-3 text-xs text-muted-foreground">
            {appliedInfo.resumeName && (
              <span className="inline-flex items-center gap-1 font-medium text-foreground/80">
                <FileText className="h-3.5 w-3.5 text-primary" />
                {appliedInfo.resumeName}
              </span>
            )}
            {appliedInfo.appliedAt && (
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3.5 w-3.5 text-primary" />
                Applied {formatDistanceToNow(new Date(appliedInfo.appliedAt), { addSuffix: true })}
              </span>
            )}
          </div>
        )}

        {showMatchScore && job.matchedSkills && job.matchedSkills.length > 0 && (
          <div className="space-y-3 pt-2 border-t">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Award className="h-4 w-4 text-accent" />
                <span className="text-sm font-medium">
                  Matched Skills ({job.matchedSkillsCount})
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {job.matchedSkills.slice(0, 6).map((skill, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {skill}
                  </Badge>
                ))}
                {job.matchedSkills.length > 6 && (
                  <Badge variant="outline" className="text-xs">
                    +{job.matchedSkills.length - 6} more
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 pt-2">
          <Badge variant="outline" className="text-xs">
            {job.source_api}
          </Badge>
        </div>
      </CardContent>

      <CardFooter>
        {appliedMode ? (
          <div className="flex w-full items-center gap-2">
            <Button disabled className="flex-1">
              Applied
            </Button>
            <Button variant="outline" size="icon" onClick={(e) => handleApply(e)}>
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <Button 
            onClick={(e) => handleApply(e)}
            className="w-full group-hover:bg-primary-hover transition-colors"
          >
            Apply Now
            <ExternalLink className="ml-2 h-4 w-4" />
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
