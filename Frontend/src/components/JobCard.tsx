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
  TrendingUp,
  Award,
} from 'lucide-react';
import { saveJobToLocalStorage } from '@/lib/api';
import { toast } from 'sonner';

interface JobCardProps {
  job: Job;
  showMatchScore?: boolean;
}

export function JobCard({ job, showMatchScore = true }: JobCardProps) {
  const handleApply = () => {
    window.open(job.url, '_blank');
    saveJobToLocalStorage(job);
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

  return (
    <Card className="group hover:shadow-card-hover transition-all duration-300 animate-fade-in">
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

        {showMatchScore && (
          <div className="space-y-3 pt-2 border-t">
            {job.matchedSkills && job.matchedSkills.length > 0 && (
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
            )}
            
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center p-2 rounded bg-primary-light">
                <TrendingUp className="h-3 w-3 mx-auto mb-1 text-primary" />
                <div className="font-semibold text-primary">
                  {job.semanticScore?.toFixed(0)}%
                </div>
                <div className="text-muted-foreground">Semantic</div>
              </div>
              <div className="text-center p-2 rounded bg-primary-light">
                <Award className="h-3 w-3 mx-auto mb-1 text-primary" />
                <div className="font-semibold text-primary">
                  {job.keywordScore?.toFixed(0)}%
                </div>
                <div className="text-muted-foreground">Keywords</div>
              </div>
              <div className="text-center p-2 rounded bg-primary-light">
                <Briefcase className="h-3 w-3 mx-auto mb-1 text-primary" />
                <div className="font-semibold text-primary">
                  {job.experienceScore?.toFixed(0)}%
                </div>
                <div className="text-muted-foreground">Experience</div>
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
        <Button 
          onClick={handleApply}
          className="w-full group-hover:bg-primary-hover transition-colors"
        >
          Apply Now
          <ExternalLink className="ml-2 h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
