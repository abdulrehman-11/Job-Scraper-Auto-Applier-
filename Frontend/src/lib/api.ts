import { Job } from '@/types/job';

const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook-test/match-resume';

// Clean up Google Sheets exported data (removes '= prefix and trims)
function cleanSheetValue(value: any): any {
  if (typeof value === 'string') {
    // Remove Google Sheets formula prefixes like "'=..." or "=..." and trim
    const cleaned = value.replace(/^'=|^=/, '').trim();
    return cleaned;
  }
  return value;
}

// Clean all job data from backend
function cleanJobData(jobs: any[]): Job[] {
  return jobs.map(job => {
    const toArray = (val: any): string[] | undefined => {
      if (Array.isArray(val)) return val.map((v) => String(cleanSheetValue(v))).filter(Boolean);
      if (typeof val === 'string') {
        const cleaned = cleanSheetValue(val);
        return cleaned
          ? cleaned.split(',').map((s) => s.trim()).filter(Boolean)
          : [];
      }
      return undefined;
    };

    const matchedSkills = toArray(job.matchedSkills);
    const missingSkills = toArray(job.missingSkills);
    const requiredSkills = toArray(job.requiredSkills);

    return {
      ...job,
      job_id: cleanSheetValue(job.job_id),
      title: cleanSheetValue(job.title),
      company: cleanSheetValue(job.company),
      location: cleanSheetValue(job.location),
      job_type: cleanSheetValue(job.job_type),
      salary: cleanSheetValue(job.salary),
      url: cleanSheetValue(job.url),
      source_api: cleanSheetValue(job.source_api),
      description: cleanSheetValue(job.description),
      matchedSkills,
      missingSkills,
      requiredSkills,
    } as Job;
  });
}

export async function uploadResumeAndMatchJobs(file: File): Promise<Job[]> {
  const formData = new FormData();
  formData.append('data', file);

  try {
    const response = await fetch(N8N_WEBHOOK_URL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to process resume: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Raw backend response:', data);
    console.log('Is array?', Array.isArray(data));
    console.log('Data length:', Array.isArray(data) ? data.length : 'N/A');
    
    // The webhook may return an array of jobs directly
    if (Array.isArray(data)) {
      const cleaned = cleanJobData(data);
      console.log('Cleaned jobs count:', cleaned.length);
      return cleaned;
    }

    // Or it might return an object with a jobs array
    if (data && typeof data === 'object') {
      if ((data as any).jobs && Array.isArray((data as any).jobs)) {
        const cleaned = cleanJobData((data as any).jobs);
        console.log('Cleaned jobs count:', cleaned.length);
        return cleaned;
      }
      // Some backends return a single job object — wrap it in an array
      const looksLikeJob = ('job_id' in (data as any)) || ('title' in (data as any) && 'company' in (data as any));
      if (looksLikeJob) {
        const cleaned = cleanJobData([data]);
        console.log('Cleaned jobs count:', cleaned.length);
        return cleaned;
      }
    }
    
    throw new Error('Unexpected response format from backend');
  } catch (error) {
    console.error('Error matching resume to jobs:', error);
    throw error;
  }
}

export function saveJobToLocalStorage(job: Job) {
  const appliedJobs = getAppliedJobsFromLocalStorage();
  const exists = appliedJobs.some(j => j.job_id === job.job_id);
  
  if (!exists) {
    appliedJobs.push({
      ...job,
      appliedAt: new Date().toISOString(),
    });
    localStorage.setItem('appliedJobs', JSON.stringify(appliedJobs));
  }
}

export function getAppliedJobsFromLocalStorage(): (Job & { appliedAt: string })[] {
  const stored = localStorage.getItem('appliedJobs');
  return stored ? JSON.parse(stored) : [];
}

export function saveMatchedJobs(jobs: Job[], resumeId: string) {
  console.log('Saving jobs:', jobs.length, 'for resume:', resumeId);
  const allJobsByResume = getAllJobsByResume();
  const batchId = Date.now().toString();
  const extractionDate = new Date().toISOString();
  
  // Get existing batches or create new array
  const existingData = allJobsByResume[resumeId];
  const batches = existingData?.batches || [];
  
  // Add new batch
  batches.push({
    batchId,
    extractionDate,
    jobs,
  });
  
  allJobsByResume[resumeId] = {
    batches,
    lastExtraction: extractionDate,
  };
  
  localStorage.setItem('jobsByResume', JSON.stringify(allJobsByResume));
}

export function getAllJobsByResume(): Record<string, { 
  batches: Array<{ batchId: string; extractionDate: string; jobs: Job[] }>;
  lastExtraction: string;
}> {
  const stored = localStorage.getItem('jobsByResume');
  return stored ? JSON.parse(stored) : {};
}

export function getMatchedJobs(): Job[] {
  const allJobsByResume = getAllJobsByResume();
  // Flatten all jobs from all resumes and batches
  const allJobs: Job[] = [];
  Object.values(allJobsByResume).forEach(({ batches }) => {
    batches.forEach(batch => {
      allJobs.push(...batch.jobs);
    });
  });
  console.log('Getting matched jobs, total:', allJobs.length);
  return allJobs;
}

export function getResumesSortedByLatest(): Array<{
  id: string;
  filename: string;
  fileUrl: string;
  uploadedAt: string;
  jobCount: number;
  lastExtraction: string;
}> {
  const resumes = getResumes();
  const allJobsByResume = getAllJobsByResume();
  
  // Add job count and last extraction date to each resume
  const resumesWithMeta = resumes.map(resume => {
    const jobData = allJobsByResume[resume.id];
    const jobCount = jobData?.batches.reduce((sum, batch) => sum + batch.jobs.length, 0) || 0;
    const lastExtraction = jobData?.lastExtraction || resume.uploadedAt;
    
    return {
      ...resume,
      jobCount,
      lastExtraction,
    };
  });
  
  // Sort by last extraction date (most recent first)
  return resumesWithMeta.sort((a, b) => 
    new Date(b.lastExtraction).getTime() - new Date(a.lastExtraction).getTime()
  );
}

export function saveResume(filename: string, fileUrl: string) {
  const resumes = getResumes();
  
  // Check if resume with same filename already exists
  const existingResume = resumes.find(r => r.filename === filename);
  
  if (existingResume) {
    // Update the uploadedAt timestamp for existing resume
    existingResume.uploadedAt = new Date().toISOString();
    localStorage.setItem('resumes', JSON.stringify(resumes));
    return existingResume;
  }
  
  // Create new resume
  const newResume = {
    id: Date.now().toString(),
    filename,
    fileUrl,
    uploadedAt: new Date().toISOString(),
  };
  resumes.push(newResume);
  localStorage.setItem('resumes', JSON.stringify(resumes));
  return newResume;
}

export function getResumes(): Array<{
  id: string;
  filename: string;
  fileUrl: string;
  uploadedAt: string;
}> {
  const stored = localStorage.getItem('resumes');
  return stored ? JSON.parse(stored) : [];
}

export function deleteResume(resumeId: string) {
  // Delete resume from resumes list
  const resumes = getResumes();
  const updatedResumes = resumes.filter(r => r.id !== resumeId);
  localStorage.setItem('resumes', JSON.stringify(updatedResumes));
  
  // Delete all jobs associated with this resume
  const allJobsByResume = getAllJobsByResume();
  delete allJobsByResume[resumeId];
  localStorage.setItem('jobsByResume', JSON.stringify(allJobsByResume));
}

export function deleteExtraction(resumeId: string, batchId: string) {
  const allJobsByResume = getAllJobsByResume();
  const resumeData = allJobsByResume[resumeId];
  
  if (!resumeData) return;
  
  // Filter out the batch to delete
  const updatedBatches = resumeData.batches.filter(b => b.batchId !== batchId);
  
  if (updatedBatches.length === 0) {
    // If no batches left, delete the entire resume entry
    delete allJobsByResume[resumeId];
  } else {
    // Update with remaining batches
    allJobsByResume[resumeId] = {
      batches: updatedBatches,
      lastExtraction: updatedBatches[0].extractionDate, // Most recent batch
    };
  }
  
  localStorage.setItem('jobsByResume', JSON.stringify(allJobsByResume));
}
