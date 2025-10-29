import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobCard } from '@/components/JobCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { getAllJobsByResume, getResumes, deleteExtraction } from '@/lib/api';
import { Search, SlidersHorizontal, ArrowLeft, FileText, Calendar, Package, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { toast } from '@/hooks/use-toast';

const ResumeJobs = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [jobsByResume, setJobsByResume] = useState(getAllJobsByResume());
  const resumes = getResumes();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('all');
  const [jobTypeFilter, setJobTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('match');
  const [selectedBatch, setSelectedBatch] = useState<string>('all');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [extractionToDelete, setExtractionToDelete] = useState<{ batchId: string; extractionDate: string; jobCount: number } | null>(null);

  const handleDeleteExtraction = () => {
    if (!extractionToDelete || !resumeId) return;
    
    deleteExtraction(resumeId, extractionToDelete.batchId);
    const updatedJobsByResume = getAllJobsByResume();
    setJobsByResume(updatedJobsByResume);
    setDeleteDialogOpen(false);
    
    // If no batches left, redirect back to resumes
    if (!updatedJobsByResume[resumeId] || updatedJobsByResume[resumeId].batches.length === 0) {
      toast({
        title: "Extraction deleted",
        description: `All jobs from this extraction have been deleted. No more extractions left for this resume.`,
      });
      navigate('/dashboard/resumes');
      return;
    }
    
    // Reset selected batch if it was the one deleted
    if (selectedBatch === extractionToDelete.batchId) {
      setSelectedBatch('all');
    }
    
    setExtractionToDelete(null);
    
    toast({
      title: "Extraction deleted",
      description: `${extractionToDelete.jobCount} jobs from this extraction have been deleted.`,
    });
  };

  const openDeleteExtractionDialog = (batch: { batchId: string; extractionDate: string; jobs: any[] }) => {
    setExtractionToDelete({
      batchId: batch.batchId,
      extractionDate: batch.extractionDate,
      jobCount: batch.jobs.length
    });
    setDeleteDialogOpen(true);
  };

  const resume = resumes.find(r => r.id === resumeId);
  const resumeData = resumeId ? jobsByResume[resumeId] : null;

  if (!resume || !resumeData) {
    return (
      <div className="text-center py-12 animate-fade-in">
        <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h2 className="text-2xl font-bold mb-2">Resume Not Found</h2>
        <p className="text-muted-foreground mb-6">
          The requested resume could not be found.
        </p>
        <Button onClick={() => navigate('/dashboard/resumes')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Resumes
        </Button>
      </div>
    );
  }

  // Get all jobs from all batches
  const allJobs = useMemo(() => {
    const jobs: any[] = [];
    resumeData.batches.forEach((batch) => {
      batch.jobs.forEach(job => {
        jobs.push({ ...job, batchId: batch.batchId, extractionDate: batch.extractionDate });
      });
    });
    return jobs;
  }, [resumeData]);

  // Get unique locations and job types
  const locations = useMemo(() => {
    const locs = [...new Set(allJobs.map(job => job.location))];
    return locs.sort();
  }, [allJobs]);

  const jobTypes = useMemo(() => {
    const types = [...new Set(allJobs.map(job => job.job_type))];
    return types.sort();
  }, [allJobs]);

  // Filter and sort jobs
  const filteredJobs = useMemo(() => {
    let filtered = allJobs.filter(job => {
      const matchesSearch = 
        job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.description.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesLocation = locationFilter === 'all' || job.location === locationFilter;
      const matchesJobType = jobTypeFilter === 'all' || job.job_type === jobTypeFilter;
      const matchesBatch = selectedBatch === 'all' || job.batchId === selectedBatch;

      return matchesSearch && matchesLocation && matchesJobType && matchesBatch;
    });

    // Sort jobs
    if (sortBy === 'match') {
      filtered.sort((a, b) => (b.hybridScore || 0) - (a.hybridScore || 0));
    } else if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.posted_date).getTime() - new Date(a.posted_date).getTime());
    } else if (sortBy === 'company') {
      filtered.sort((a, b) => a.company.localeCompare(b.company));
    }

    return filtered;
  }, [allJobs, searchQuery, locationFilter, jobTypeFilter, sortBy, selectedBatch]);

  // Group jobs by batch for display
  const groupedByBatch = useMemo(() => {
    const grouped: Record<string, any[]> = {};
    filteredJobs.forEach(job => {
      if (!grouped[job.batchId]) {
        grouped[job.batchId] = [];
      }
      grouped[job.batchId].push(job);
    });
    return grouped;
  }, [filteredJobs]);

  // Sort batches by extraction date (newest first)
  const sortedBatches = useMemo(() => {
    return resumeData.batches
      .slice()
      .sort((a, b) => new Date(b.extractionDate).getTime() - new Date(a.extractionDate).getTime());
  }, [resumeData.batches]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="space-y-4">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/dashboard/resumes')}
          className="mb-2"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Resumes
        </Button>
        
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold">{resume.filename}</h1>
                <p className="text-muted-foreground">
                  {filteredJobs.length} {filteredJobs.length === 1 ? 'job' : 'jobs'} found
                  {selectedBatch !== 'all' && ' in selected extraction'}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-sm">
              <Package className="mr-1 h-3 w-3" />
              {resumeData.batches.length} {resumeData.batches.length === 1 ? 'extraction' : 'extractions'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Batch Filter */}
      {resumeData.batches.length > 1 && (
        <Card className="p-4 bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20">
          <div className="flex items-center gap-3 flex-wrap">
            <Calendar className="h-5 w-5 text-primary" />
            <Select value={selectedBatch} onValueChange={setSelectedBatch}>
              <SelectTrigger className="w-[320px]">
                <SelectValue placeholder="Filter by extraction date" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Extractions ({allJobs.length} jobs)</SelectItem>
                {sortedBatches.map((batch, index) => (
                  <SelectItem key={batch.batchId} value={batch.batchId}>
                    {index === 0 ? '🆕 ' : ''}
                    {new Date(batch.extractionDate).toLocaleDateString()} - {batch.jobs.length} jobs
                    {' '}({formatDistanceToNow(new Date(batch.extractionDate), { addSuffix: true })})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </Card>
      )}

      {/* Filters */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="md:col-span-2 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search jobs, companies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        <Select value={locationFilter} onValueChange={setLocationFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Location" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Locations</SelectItem>
            {locations.map(loc => (
              <SelectItem key={loc} value={loc}>{loc}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={jobTypeFilter} onValueChange={setJobTypeFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Job Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {jobTypes.map(type => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Sort */}
      <div className="flex items-center gap-2">
        <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Sort by:</span>
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="match">Best Match</SelectItem>
            <SelectItem value="date">Latest</SelectItem>
            <SelectItem value="company">Company</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Jobs Display */}
      {filteredJobs.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No jobs match your filters</p>
        </div>
      ) : selectedBatch === 'all' && resumeData.batches.length > 1 ? (
        // Group by batch when showing all
        <div className="space-y-8">
          {sortedBatches
            .filter(batch => groupedByBatch[batch.batchId]?.length > 0)
            .map((batch, index) => {
              const batchJobs = groupedByBatch[batch.batchId];
              return (
                <div key={batch.batchId} className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b-2 border-primary/20">
                    <div className="flex items-center gap-3">
                      <Badge variant={index === 0 ? 'default' : 'secondary'} className="text-sm">
                        {index === 0 ? '🆕 Latest' : `Extraction ${sortedBatches.length - index}`}
                      </Badge>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span className="text-sm">
                          {new Date(batch.extractionDate).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                        <span className="text-xs">
                          ({formatDistanceToNow(new Date(batch.extractionDate), { addSuffix: true })})
                        </span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        • {batchJobs.length} jobs
                      </span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="hover:bg-destructive hover:text-destructive-foreground transition-colors border-destructive/30"
                      onClick={() => openDeleteExtractionDialog(batch)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Extraction
                    </Button>
                  </div>
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {batchJobs.map((job) => (
                      <JobCard key={`${job.job_id}-${job.batchId}`} job={job} showMatchScore />
                    ))}
                  </div>
                </div>
              );
            })}
        </div>
      ) : (
        // Simple grid when filtering by single batch
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredJobs.map((job) => (
            <JobCard key={`${job.job_id}-${job.batchId}`} job={job} showMatchScore />
          ))}
        </div>
      )}

      {/* Delete Extraction Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this extraction section with <strong>{extractionToDelete?.jobCount} job{extractionToDelete?.jobCount !== 1 ? 's' : ''}</strong> from{' '}
              {extractionToDelete && new Date(extractionToDelete.extractionDate).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteExtraction}
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

export default ResumeJobs;
