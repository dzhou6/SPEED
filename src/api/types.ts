export type Role = "Frontend" | "Backend" | "Matching" | "Platform";
export type RolePref = Role;

export type SwipeDecision = "accept" | "pass";

export type SwipeRequest = {
  courseCode: string;
  userId: string;
  targetUserId: string;
  decision: SwipeDecision;
};

export type SetHubRequest = {
  courseCode: string;
  userId: string;
  hubLink: string;
};

export type ContactInfo = {
  discord?: string;
  linkedin?: string;
};

export type ProfileUpsertRequest = {
  courseCode: string;
  displayName?: string;
  rolePrefs: Role[];
  skills: string[];
  availability: string[];
  goals?: string;
  contact?: ContactInfo; // optional (backend may ignore unless you add it server-side)
};

export type RecommendationUser = {
  userId: string;
  displayName: string;
  rolePrefs: Role[];
  skills: string[];
  availability: string[];
  lastActiveAt?: string | null;
  score?: number;
  reasons?: string[];
};

export type RecommendationsResponse = {
  candidates: RecommendationUser[];
};

export type PodMember = {
  userId: string;
  displayName: string;
  rolePrefs: Role[];
  skills: string[];
  availability: string[];
  lastActiveAt?: string | null;
};

export type PodState =
  | { hasPod: false }
  | {
      hasPod: true;
      podId: string;
      courseCode: string;
      leaderId: string;
      memberIds: string[];
      members: PodMember[];
      unlockedContactIds: string[];
      hubLink?: string | null;
    };

export type AskResponse = {
  layer: number;
  answer: string;
  links: string[];
};

export type CourseInfo = {
  courseCode: string;
  courseName?: string;
  syllabusText?: string;
  professor?: string;
  location?: string;
  classPolicy?: string;
  latePolicy?: string;
  officeHours?: string;
};

export type UserCoursesResponse = {
  courseCodes: string[];
  courses?: Array<{
    courseCode: string;
    courseName?: string;
  }>;
};
