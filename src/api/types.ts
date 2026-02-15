// src/api/types.ts

export type Role =
  | "Frontend"
  | "Backend"
  | "Matching"
  | "Platform"
  | "DevOps"
  | "Design"
  | "Other";

export type RolePref = Role;

export type SwipeDecision = "accept" | "pass";

export interface ContactInfo {
  discord?: string | null;
  linkedin?: string | null;

  // some pages reference contact.email, so allow it
  email?: string | null;
}

// Used by MatchFeed cards
export interface RecommendationUser {
  userId: string;

  displayName?: string;
  bio?: string | null;

  // keep both to avoid frontend/back-end naming mismatches during hackathon
  rolePrefs?: Role[];
  roles?: Role[];

  // MatchFeed currently uses these
  skills?: string[];
  availability?: string[];
  reasons?: string[];

  // “lastActiveAt” is canonical; allow null/undefined
  lastActiveAt?: string | null;

  // optional legacy convenience field (if you still use it somewhere)
  lastActive?: string;

  // anything else the backend might attach
  score?: number;
}

// Used by Pod page member list
export interface PodMember {
  userId: string;
  displayName?: string;

  rolePrefs?: Role[];
  roles?: Role[];

  skills?: string[];
  availability?: string[];

  mutualAccepted?: boolean;

  // your PodPage checks this
  contactUnlocked?: boolean;

  // last-active fields that some UIs compute/display
  lastActiveAt?: string | null;
  lastActive?: string;

  contact?: ContactInfo;
}

// IMPORTANT: keep PodState as a single interface (not a union)
export interface PodState {
  hasPod: boolean;

  podId?: string;
  courseCode?: string;

  members?: PodMember[];

  leaderUserId?: string;
  hubLink?: string | null;

  unlockedContactIds?: string[];
}

export interface RecommendationsResponse {
  // some code uses rec.candidates, some uses rec.recommendations
  candidates?: RecommendationUser[];
  recommendations?: RecommendationUser[];
  pod?: PodState;
}

export interface SwipeRequest {
  userId: string; // actor (current user)
  courseCode: string;
  targetUserId: string;
  decision: SwipeDecision;
}

export interface SetHubRequest {
  userId: string;
  courseCode: string;
  hubLink: string;
}

export type AskLink = { title?: string; url: string };

export interface AskResponse {
  answer: string;
<<<<<<< HEAD
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
=======

  // PodPage references these
  layer?: string;
  links?: Array<string | AskLink>;
}

// JoinCourse.tsx expects res.displayName
export interface DemoAuthResponse {
  userId: string;
  courseCode: string;
  token?: string;
  displayName?: string;
}

export interface TicketResponse {
  ok: boolean;
  ticketId?: string;
  message?: string;
}
>>>>>>> 6ea5624 (Fix frontend build and connect backend to Atlas)
