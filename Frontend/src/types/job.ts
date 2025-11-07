export interface Job {
  job_id: string;
  title: string;
  company: string;
  location: string;
  job_type: string;
  salary: string;
  url: string;
  source_api: string;
  posted_date: string;
  description: string;
  
  // Matching scores
  hybridScore?: number;
  semanticScore?: number;
  keywordScore?: number;
  experienceScore?: number;
  
  // Skill matching
  matchedSkills?: string[];
  missingSkills?: string[];
  matchedSkillsCount?: number;
  requiredSkills?: string[];
  requiredSkillsCount?: number;
  skillMatchPercentage?: number;
  
  // Candidate context
  candidateExperience?: number;
  candidateSeniority?: string;
  requiredExperience?: number;
  
  // Ranking
  rank?: number;

  // Local metadata
  resumeId?: string;
  resumeFilename?: string;
  batchId?: string;
  extractionDate?: string;
}

export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  file_url: string;
  uploaded_at: string;
  parsed_data?: {
    skills: string[];
    experience_years: number;
    seniority: string;
    primary_domain: string;
  };
}

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  applied_at: string;
  status: 'applied' | 'viewed' | 'interviewing' | 'rejected' | 'accepted';
}
