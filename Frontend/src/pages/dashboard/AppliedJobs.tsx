import { JobCard } from '@/components/JobCard';
import { getAppliedJobsFromLocalStorage } from '@/lib/api';
import { CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const AppliedJobs = () => {
  const appliedJobs = getAppliedJobsFromLocalStorage();
  const sortedAppliedJobs = appliedJobs
    .slice()
    .sort((a, b) => {
      const resumeA = (a.resumeFilename || '').toLowerCase();
      const resumeB = (b.resumeFilename || '').toLowerCase();
      if (resumeA !== resumeB) {
        return resumeA.localeCompare(resumeB);
      }
      return new Date(b.appliedAt).getTime() - new Date(a.appliedAt).getTime();
    });

  if (sortedAppliedJobs.length === 0) {
    return (
      <div className="text-center py-12 animate-fade-in">
        <CheckCircle className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h2 className="text-2xl font-bold mb-2">No Applications Yet</h2>
        <p className="text-muted-foreground">
          Start applying to jobs and track them here
        </p>
      </div>
    );
  }

  const groupedByResume = sortedAppliedJobs.reduce<Record<string, typeof sortedAppliedJobs>>((acc, job) => {
    const key = job.resumeFilename || 'Unknown resume';
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(job);
    return acc;
  }, {});

  const resumeOrder = Object.keys(groupedByResume).sort((a, b) => {
    if (a === 'Unknown resume') return 1;
    if (b === 'Unknown resume') return -1;
    return a.localeCompare(b);
  });

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Applied Jobs</h1>
        <p className="text-muted-foreground">
          You have applied to {sortedAppliedJobs.length} {sortedAppliedJobs.length === 1 ? 'job' : 'jobs'}
        </p>
      </div>

      {resumeOrder.map((resumeName) => {
        const jobsForResume = groupedByResume[resumeName].slice().sort((a, b) => new Date(b.appliedAt).getTime() - new Date(a.appliedAt).getTime());
        return (
          <div key={resumeName} className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-semibold">
                  {resumeName === 'Unknown resume' ? 'Other applications' : resumeName}
                </h2>
                <Badge variant="secondary" className="text-xs">
                  {jobsForResume.length} {jobsForResume.length === 1 ? 'job' : 'jobs'}
                </Badge>
              </div>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {jobsForResume.map((job) => (
                <JobCard
                  key={`${job.job_id}-${job.appliedAt}`}
                  job={job}
                  showMatchScore
                  appliedMode
                  appliedMetadata={{
                    appliedAt: job.appliedAt,
                    resumeName: job.resumeFilename || (resumeName === 'Unknown resume' ? undefined : resumeName),
                  }}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AppliedJobs;
