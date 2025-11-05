import { JobCard } from '@/components/JobCard';
import { getAppliedJobsFromLocalStorage } from '@/lib/api';
import { CheckCircle } from 'lucide-react';

const AppliedJobs = () => {
  const appliedJobs = getAppliedJobsFromLocalStorage();

  if (appliedJobs.length === 0) {
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

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Applied Jobs</h1>
        <p className="text-muted-foreground">
          You have applied to {appliedJobs.length} {appliedJobs.length === 1 ? 'job' : 'jobs'}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {appliedJobs.map((job) => (
          <div key={job.job_id} className="relative">
            <JobCard job={job} showMatchScore appliedMode />
          </div>
        ))}
      </div>
    </div>
  );
};

export default AppliedJobs;
