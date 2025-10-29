import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getMatchedJobs, getAppliedJobsFromLocalStorage } from '@/lib/api';
import { 
  Briefcase, 
  TrendingUp, 
  CheckCircle, 
  Upload,
  Target,
  Award,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const DashboardHome = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const matchedJobs = getMatchedJobs();
  const appliedJobs = getAppliedJobsFromLocalStorage();

  const stats = [
    {
      title: 'Matched Jobs',
      value: matchedJobs.length,
      icon: Briefcase,
      color: 'text-primary',
      bgColor: 'bg-primary-light',
    },
    {
      title: 'Applied',
      value: appliedJobs.length,
      icon: CheckCircle,
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      title: 'Avg Match Score',
      value: matchedJobs.length > 0 
        ? `${Math.round(matchedJobs.reduce((sum, job) => sum + (job.hybridScore || 0), 0) / matchedJobs.length)}%`
        : 'N/A',
      icon: TrendingUp,
      color: 'text-primary',
      bgColor: 'bg-primary-light',
    },
  ];

  const topJobs = matchedJobs.slice(0, 3);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {user?.name}! 👋
        </h1>
        <p className="text-muted-foreground">
          Here's your job matching overview
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.title} className="hover:shadow-card-hover transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      {matchedJobs.length === 0 ? (
        <Card className="border-dashed border-2">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 p-3 rounded-full bg-primary-light w-fit">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            <CardTitle>Get Started</CardTitle>
            <CardDescription>
              Upload your resume to find perfect job matches
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => navigate('/resume-upload')} size="lg">
              <Upload className="mr-2 h-4 w-4" />
              Upload Resume
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Top Matches */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Top Matches</CardTitle>
                  <CardDescription>Your best job opportunities</CardDescription>
                </div>
                <Award className="h-5 w-5 text-accent" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {topJobs.map((job) => (
                <div
                  key={job.job_id}
                  className="p-4 border rounded-lg hover:bg-secondary/50 transition-colors cursor-pointer"
                  onClick={() => navigate('/dashboard/resumes')}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold">{job.title}</h4>
                      <p className="text-sm text-muted-foreground">{job.company}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-primary">
                        {job.hybridScore?.toFixed(0)}%
                      </div>
                      <div className="text-xs text-muted-foreground">match</div>
                    </div>
                  </div>
                </div>
              ))}
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => navigate('/dashboard/resumes')}
              >
                View All Jobs
              </Button>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Applications</CardTitle>
                  <CardDescription>Your latest job applications</CardDescription>
                </div>
                <Target className="h-5 w-5 text-primary" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {appliedJobs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No applications yet</p>
                  <p className="text-sm">Start applying to jobs!</p>
                </div>
              ) : (
                <>
                  {appliedJobs.slice(0, 3).map((job) => (
                    <div
                      key={job.job_id}
                      className="p-4 border rounded-lg hover:bg-secondary/50 transition-colors"
                    >
                      <h4 className="font-semibold">{job.title}</h4>
                      <p className="text-sm text-muted-foreground">{job.company}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Applied {new Date(job.appliedAt).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => navigate('/dashboard/applied')}
                  >
                    View All Applications
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DashboardHome;
