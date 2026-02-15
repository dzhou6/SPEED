export type Role = "Frontend" | "Backend" | "Designer" | "PM" | "Tester";

export interface DemoAuthResponse {
  userId: string;
  displayName?: string;
}

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

export type ContactInfo = {
  email?: string;
  discord?: string;
  linkedin?: string;
};

export type Profile = {
  displayName?: string;
  rolePrefs?: Role[];
  skills?: string[];
  availability?: string[];
  goals?: string | null;
  contact?: ContactInfo | null;
};

export type RecommendationUser = {
  userId: string;
  displayName: string;
  rolePrefs: Role[];
  skills: string[];
  availability: string[];
  lastActiveAt?: string | null;
  score: number;
  reasons: string[];
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
      leaderId?: string;
      leaderUserId?: string;
      members: PodMember[];
      memberIds?: string[];
      unlockedContactIds?: string[];
      hubLink?: string | null;
    };

export type SwipeRequest = {
  courseCode: string;
  targetUserId: string;
  decision: "accept" | "pass";
};

export type SetHubRequest = {
  courseCode: string;
  hubLink: string;
};

export type AskResponse = {
  layer: 1 | 2 | 3;
  answer: string;
  links?: Array<{ title: string; url: string }> | string[];
};

export type TicketResponse = {
  ok?: boolean;
  ticketId?: string;
  message?: string;
};
